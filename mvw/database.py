import sqlite3
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
            review TEXT,
            rt_tomatometer INTEGER,
            rt_audience_score INTEGER,
            rt_certification TEXT,
            rt_critic_reviews INTEGER,
            rt_audience_reviews INTEGER
        );
    '''

TABLE_COLUMNS = [
    "imdbid", "title", "year", "rated", "released", "runtime", "genre",
    "director", "writer", "actors", "plot", "language", "country", "awards",
    "poster_link", "metascore", "imdbrating", "imdbvotes", "type", "dvd",
    "boxoffice", "production", "website", "poster_local_path", "star", "review",
    "rt_tomatometer", "rt_audience_score", "rt_certification", "rt_critic_reviews",
    "rt_audience_reviews",
]

INT_COLUMNS = {"rt_tomatometer", "rt_audience_score", "rt_critic_reviews", "rt_audience_reviews"}

def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for col in INT_COLUMNS:
        if col in d and d[col] is not None:
            try:
                d[col] = int(d[col])
            except (ValueError, TypeError):
                pass
    return d

class DatabaseManager:
    def __init__(self) -> None:
        self.conn = sqlite3.connect(path.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.initialize_db()
        atexit.register(self.close_db)

    def initialize_db(self):
        cursor = self.conn.cursor()
        cursor.execute(INIT_TABLE)
        self._migrate_schema(cursor)
        self.conn.commit()

    def _migrate_schema(self, cursor):
        cursor.execute("PRAGMA table_info(movies)")
        existing = {row[1] for row in cursor.fetchall()}
        for col in TABLE_COLUMNS:
            if col not in existing:
                kind = "INTEGER" if col in ("rt_tomatometer", "rt_audience_score", "rt_critic_reviews", "rt_audience_reviews") else "TEXT"
                cursor.execute(f"ALTER TABLE movies ADD COLUMN {col} {kind}")

    def store_movie_metadata(self, movie, poster_local_path: str, star: float, review: str):
        try:
            cursor = self.conn.cursor()
            # Note: We include poster_local_path, star, and review in the values list
            cursor.execute('''
                INSERT INTO movies (
                    title, year, rated, released, runtime, genre, director, writer,
                    actors, plot, language, country, awards, poster_link, metascore,
                    imdbrating, imdbvotes, imdbid, type, dvd, boxoffice, production,
                    website, poster_local_path, star, review,
                    rt_tomatometer, rt_audience_score, rt_certification, rt_critic_reviews, rt_audience_reviews
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?)
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
                    review=excluded.review,
                    rt_tomatometer=excluded.rt_tomatometer,
                    rt_audience_score=excluded.rt_audience_score,
                    rt_certification=excluded.rt_certification,
                    rt_critic_reviews=excluded.rt_critic_reviews,
                    rt_audience_reviews=excluded.rt_audience_reviews
            ''',(
                    movie['title'], movie['year'], movie['rated'], movie['released'],
                    movie['runtime'], movie['genre'], movie['director'], movie['writer'],
                    movie['actors'], movie['plot'], movie['language'], movie['country'],
                    movie['awards'], movie['poster'], movie['metascore'], movie['imdbrating'],
                    movie['imdbvotes'], movie['imdbid'], movie['type'], movie['dvd'],
                    movie['boxoffice'], movie['production'], movie['website'], poster_local_path, star, review,
                    movie.get('rt_tomatometer'), movie.get('rt_audience_score'),
                    movie.get('rt_certification'), movie.get('rt_critic_reviews'),
                    movie.get('rt_audience_reviews')
                )
            )
            if ConfigManager().get_config("DATA", "worldwide_boxoffice").lower() == "true":
                new_boxoffice = self.set_movie_boxoffice_to_worldwide(movie['imdbid'])
                if new_boxoffice:
                    movie['boxoffice'] = new_boxoffice

            if not movie.get('rt_tomatometer'):
                rt_data = movie_manager.fetch_rt_data(
                    movie['title'], movie['year'],
                    tomato_url=movie.get('tomato_url')
                )
                if rt_data and rt_data.get('rt_tomatometer') is not None:
                    movie.update(rt_data)
                    from .rt import normalize_review_count
                    critic_fmt = normalize_review_count(rt_data.get('rt_critic_reviews'))
                    audience_fmt = normalize_review_count(rt_data.get('rt_audience_reviews'))
                    moai.says(
                        f"[yellow]✓ I just searched (rottentomatoes.com) and found the RT scores "
                        f"-> Tomatometer: [bold]{rt_data['rt_tomatometer']}%[/bold], "
                        f"Audience: [bold]{rt_data['rt_audience_score']}%[/bold]\n"
                        f"               Critic reviews: {critic_fmt}, Audience reviews: {audience_fmt}\n"
                        f"               ref: [sky_blue2 underline]{movie.get('tomato_url', 'https://www.rottentomatoes.com/m/' + movie['title'].lower().replace(' ', '_'))}[/]",
                        type="nerd"
                    )

            self.conn.commit()

            moai.says(f"[green]✓ {movie['title']} [italic]saved[/italic] successfully[/]", type="fun")
        except Exception as e:
            self.conn.rollback()
            moai.says(f"[indian_red]x Sorry, Database error: ({e}) occured[/]\n[dim]This should not happen, up an issue to the dev[/]", type="error")

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
            moai.says(f"[indian_red]x Sorry, Database error: ({e}) occured[/]\n[dim]This should not happen, up an issue to the dev[/]", type="error")

    def get_all_movies(self):
        """Get all movies in the database"""
        query = """
            SELECT * FROM movies
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        return [_row_to_dict(row) for row in cursor.fetchall()]

    def get_movie_metadata_by_title(self, title: str):
        """Fetch a movie and all its genres in single query"""
        query = """
            SELECT * FROM movies WHERE title=?
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (title,))
        row = cursor.fetchone()

        return _row_to_dict(row) if row else None

    def get_movie_metadata_by_imdbid(self, imdbid: str):
        """Fetch a movie and all its genres in single query"""
        query = """
            SELECT * FROM movies WHERE imdbid=?
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (imdbid,))
        row = cursor.fetchone()

        return _row_to_dict(row) if row else None

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
                moai.says(f"[green]✓ Movie ({title}) [italic]deleted[/italic] successfully[/]", type="fun")
            else:
                moai.says(f"[indian_red]x Sorry, Movie not found[/]", type="error")
        except Exception as e:
            moai.says(f"[indian_red]x Sorry, Database error: ({e}) occured[/]", type="error")
            self.conn.rollback()

    def delete_movie_entry_by_id(self, imdbid: str):
        """Delete the movie entry using its title"""
        query = """
            DELETE FROM movies WHERE imdbid = ?
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (imdbid,))

            # IMPORTANT: You must commit to save the deletion
            self.conn.commit()

            # Check if anything was actually deleted
            if cursor.rowcount > 0:
                moai.says(f"[green]✓ Movie with IMDB_ID ({imdbid}) [italic]deleted[/italic] successfully[/]", type="fun")
            else:
                moai.says(f"[indian_red]x Sorry, Movie not found[/]", type="error")
        except Exception as e:
            moai.says(f"[indian_red]x Sorry, Database error: ({e}) occured[/]", type="error")
            self.conn.rollback()

    def set_movie_boxoffice_to_worldwide(self, imdbid: str):
        """Save the worldwide box office"""
        worldwide_value = movie_manager.fetch_box_office_worldwide(imdbid)
        if not worldwide_value:
            moai.says(f"[indian_red]x Sorry, There is no worldwide boxoffice for this entry", type="error")
            return
        try:
            query = """
                UPDATE movies SET boxoffice = ? WHERE imdbid = ?
            """
            cursor = self.conn.cursor()
            cursor.execute(query, (worldwide_value, imdbid,))
            self.conn.commit()
            moai.says(
                    f"[yellow]✓ I just searched (boxofficemojo.com) and found the global boxoffice -> [bold]{worldwide_value}[/bold]\n"
                    f"               ref: [sky_blue2 underline]https://www.boxofficemojo.com/title/{imdbid}[/]",
                    type="nerd"
                )
            return worldwide_value
        except Exception as e:
            moai.says(f"[indian_red]x Sorry, Database error: ({e}) occured[/]\n[dim]This should not happen, up an issue to the dev[/]", type="error")
            return

    def set_rt_scores(self, imdbid: str, rt_data: dict):
        """Update all RT score fields in a single query"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE movies SET
                    rt_tomatometer = ?,
                    rt_audience_score = ?,
                    rt_certification = ?,
                    rt_critic_reviews = ?,
                    rt_audience_reviews = ?
                WHERE imdbid = ?
            ''', (
                rt_data.get("rt_tomatometer"),
                rt_data.get("rt_audience_score"),
                rt_data.get("rt_certification"),
                rt_data.get("rt_critic_reviews"),
                rt_data.get("rt_audience_reviews"),
                imdbid,
            ))
            self.conn.commit()
            moai.says("[green]✓ Rotten Tomatoes scores [italic]updated[/italic] successfully[/]", type="fun")
        except Exception as e:
            moai.says(f"[indian_red]x Sorry, Database error: ({e}) occured[/]\n[dim]This should not happen, up an issue to the dev[/]", type="error")

    def set_key_value(self, identifier, attribute, value, use_title=False):
        """Set the attribute category in database with value"""
        id_column = "title" if use_title else "imdbid"
        query = f"UPDATE movies SET {attribute} = ? WHERE {id_column} = ?"
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (value, identifier))
            self.conn.commit()
            moai.says(f"[green]✓ Database ({attribute}: {value}) [italic]updated[/italic] successfully[/]", type="fun")
        except Exception as e:
            moai.says(f"[indian_red]x Sorry, Database error: ({e}) occured[/]\n[dim]This should not happen, up an issue to the dev[/]", type="error")

    def get_debug_info(self):
        """Return a dict of database diagnostics"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM movies")
        movie_count = cursor.fetchone()[0]
        cursor.execute("PRAGMA table_info(movies)")
        schema = {row[1]: row[2] for row in cursor.fetchall()}
        cursor.execute("SELECT COUNT(*) FROM movies WHERE rt_tomatometer IS NULL")
        missing_rt = cursor.fetchone()[0]
        cursor.execute("SELECT title, imdbid, rt_tomatometer FROM movies ORDER BY title")
        movies = [dict(row) for row in cursor.fetchall()]
        return {
            "db_path": str(self.conn.execute("PRAGMA database_list").fetchone()[2]),
            "movie_count": movie_count,
            "schema": schema,
            "missing_rt_count": missing_rt,
            "movies": movies,
        }

    def close_db(self):
        """Call this when the cli shuts down"""
        if self.conn:
            self.conn.close()
