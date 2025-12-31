import sqlite3
from pathlib import Path
import atexit

from mvw.config import ConfigManager

from .movie import MovieManager
from .moai import Moai
from .path import PathManager

movie_manager = MovieManager()
moai = Moai()
path = PathManager()

INIT_TABLE = '''
        CREATE TABLE IF NOT EXISTS movies (
            imdbid TEXT PRIMARY KEY,
            title TEXT,
            year TEXT,
            rated TEXT,
            released TEXT,
            runtime TEXT,
            genre TEXT,
            director TEXT,
            writer TEXT,
            actors TEXT,
            plot TEXT,
            language TEXT,
            country TEXT,
            awards TEXT,
            poster_link TEXT,
            metascore TEXT,
            imdbrating REAL,
            imdbvotes TEXT,
            type TEXT,
            dvd TEXT,
            boxoffice TEXT,
            production TEXT,
            website TEXT,
            poster_local_path TEXT,
            star TEXT,
            review TEXT
        );
    '''

class DatabaseManager:
    def __init__(self) -> None:
        self.conn = sqlite3.connect(path.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.initialize_db()
        atexit.register(self.close_db)

    def initialize_db(self):
        cursor = self.conn.cursor()
        cursor.execute(INIT_TABLE)
        self.conn.commit()

    def store_movie_metadata(self, movie, poster_local_path: str, star: float, review: str):
        try:
            cursor = self.conn.cursor()
            # Note: We include poster_local_path, star, and review in the values list
            cursor.execute('''
                INSERT INTO movies (
                    title, year, rated, released, runtime, genre, director, writer, 
                    actors, plot, language, country, awards, poster_link, metascore, 
                    imdbrating, imdbvotes, imdbid, type, dvd, boxoffice, production, 
                    website, poster_local_path, star, review
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(imdbid) DO UPDATE SET
                    title=excluded.title,
                    year=excluded.year,
                    rated=excluded.rated,
                    released=excluded.released,
                    runtime=excluded.runtime,
                    genre=excluded.genre,
                    director=excluded.director,
                    writer=excluded.writer,
                    actors=excluded.actors,
                    plot=excluded.plot,
                    language=excluded.language,
                    country=excluded.country,
                    awards=excluded.awards,
                    poster_link=excluded.poster_link,
                    metascore=excluded.metascore,
                    imdbrating=excluded.imdbrating,
                    imdbvotes=excluded.imdbvotes,
                    type=excluded.type,
                    dvd=excluded.dvd,
                    boxoffice=excluded.boxoffice,
                    production=excluded.production,
                    website=excluded.website,
                    poster_local_path=excluded.poster_local_path,
                    star=excluded.star,
                    review=excluded.review
            ''',(
                    movie['title'], movie['year'], movie['rated'], movie['released'], 
                    movie['runtime'], movie['genre'], movie['director'], movie['writer'], 
                    movie['actors'], movie['plot'], movie['language'], movie['country'], 
                    movie['awards'], movie['poster'], movie['metascore'], movie['imdbrating'], 
                    movie['imdbvotes'], movie['imdbid'], movie['type'], movie['dvd'], 
                    movie['boxoffice'], movie['production'], movie['website'], poster_local_path, star, review
                )
            )
            self.conn.commit()

            if ConfigManager().get_config("DATA", "worldwide_boxoffice").lower() == "true":
                self.set_movie_boxoffice_to_worldwide(movie['imdbid'])

            moai.says(f"[green]✓ {movie['title']} [italic]saved[/italic] successfully[/]")
        except Exception as e:
            self.conn.rollback()
            moai.says(f"[indian_red]x Sorry, Database error: ({e}) occured[/]\n[dim]This should not happen, up an issue to the dev[/]")

    def update_star_review(self, imdbid: str, star: float, review: str):
        """Update ONLY the star and review based on the IMDB ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE movies 
                SET star = ?, review = ?
                WHERE imdbid = ?
            ''', (star, review, imdbid))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            moai.says(f"[indian_red]x Sorry, Database error: ({e}) occured[/]\n[dim]This should not happen, up an issue to the dev[/]")

    def get_all_movies(self):
        """Get all movies in the database"""
        query = """
            SELECT * FROM movies
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def get_movie_metadata_by_title(self, title: str):
        """Fetch a movie and all its genres in single query"""
        query = """
            SELECT * FROM movies WHERE title=?
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (title,))
        row = cursor.fetchone()

        return row

    def get_movie_metadata_by_imdbid(self, imdbid: str):
        """Fetch a movie and all its genres in single query"""
        query = """
            SELECT * FROM movies WHERE imdbid=?
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (imdbid,))
        row = cursor.fetchone()

        return row

    def delete_movie_entry_by_title(self, title: str):
        """Delete the movie entry using its title"""
        query = """
            DELETE FROM movies WHERE title = ?
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (title,))

            # IMPORTANT: You must commit to save the deletion
            self.conn.commit()

            # Check if anything was actually deleted
            if cursor.rowcount > 0:
                moai.says(f"[green]✓ Movie ({title}) [italic]deleted[/italic] successfully[/]")
            else:
                moai.says(f"[indian_red]x Sorry, Movie not found[/]")
        except Exception as e:
            moai.says(f"[indian_red]x Sorry, Database error: ({e}) occured[/]")
            self.conn.rollback()

    def delete_movie_entry_by_id(self, imdbid: str):
        """Delete the movie entry using its title"""
        query = """
            DELETE FROM movies WHERE title = ?
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (imdbid,))

            # IMPORTANT: You must commit to save the deletion
            self.conn.commit()

            # Check if anything was actually deleted
            if cursor.rowcount > 0:
                moai.says(f"[green]✓ Movie with IMDB_ID ({imdbid}) [italic]deleted[/italic] successfully[/]")
            else:
                moai.says(f"[indian_red]x Sorry, Movie not found[/]")
        except Exception as e:
            moai.says(f"[indian_red]x Sorry, Database error: ({e}) occured[/]")
            self.conn.rollback()

    def set_movie_boxoffice_to_worldwide(self, imdbid: str):
        """Save the worldwide box office"""
        worldwide_value = movie_manager.fetch_box_office_worldwide(imdbid)
        if not worldwide_value:
            moai.says(f"[indian_red]x Sorry, There is no worldwide boxoffice for this entry")
            return
        query = """
            UPDATE movies SET boxoffice = ? WHERE imdbid = ?
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (worldwide_value, imdbid,))
            self.conn.commit()
        except Exception as e:
            moai.says(f"[indian_red]x Sorry, Database error: ({e}) occured[/]\n[dim]This should not happen, up an issue to the dev[/]")

    def close_db(self):
        """Call this when the cli shuts down"""
        if self.conn:
            self.conn.close()
