import requests
import re
import os
from .moai import Moai

moai = Moai()

class API:
    def __init__(self, api_key: str) -> None:
        self.api_key: str = api_key
        self.search_movies: dict = {}
        self.selected_movie: dict = {}
        self.omdb_url = 'http://www.omdbapi.com/'

    def fetch_movie_metadata(self, imdbid:str, plot=None, silent=False):
        """Get all the data movie"""
        parameters = {
            'i': imdbid,
            'plot': plot,
            'r': 'json',
            'apikey': self.api_key
        }
        result = requests.get(self.omdb_url, params=parameters).json()

        if result.pop('Response') == 'False':
            if not silent:
                moai.says(f"[indian_red]x Sorry, API error: ({result['Error']}) occured\n[dim]This should not happen, up an issue to the dev[/]", type="error")
            return self.selected_movie

        for key, value in result.items():
            key = key.lower()
            setattr(self, key, value)
            self.selected_movie[key] = value

        return self.selected_movie

    def search_movie(self, title):
        """Search and return any movies that may relate to the title"""
        # NOTE:
        # "* [cyan]movie[/]         [dim]# standard[/]\n"
        # "* [cyan]imdbid[/]        [dim]# include 'tt'[/]"

        is_imdb = re.match(r'^tt\d+$', title.strip().lower())

        parameters = {
            'type': 'movie',
            'r': 'json',
            'apikey': self.api_key
        }

        if is_imdb:
            parameters['i'] = title.strip()
        else:
            parameters['s'] = title

        try:
            result = requests.get(self.omdb_url, params=parameters).json()
        except Exception as e:
            moai.says(f"[indian_red]x Sorry, Connection error: ({e}) occured[/]", type="error")
            return self.search_movies

        if result.get('Response') == 'False':
            if str(result['Error']) == "Too many results.":
                moai.says(
                    f"[yellow]x Ermm.. actually there many movies with similar names.[/]\n"
                    "             [dim]Try search with imdbid:[/] [yellow]tt..[/]",
                    type="nerd"
                )
            else:
                moai.says(f"[indian_red]x Sorry, API error: ({result['Error']}) occured\n[dim]This should not happen, up an issue to the dev[/]", type="error")
            os.abort()

        for key, value in result.items():
            key = key.lower()
            setattr(self, key, value)
            self.search_movies[key] = value

        return self.search_movies

if __name__ == "__main__":
    from .config import ConfigManager
    api_key = str(ConfigManager().get_config("API", "omdb_api_key"))
    api = API(api_key)

    from iterfzf import iterfzf

    results = api.search_movie("up")
    movies = results.get('search', [])

    movie_map = {f"{m['Title']} ({m['Year']})": m['imdbID'] for m in movies}

    choice = iterfzf(
        list(movie_map.keys())
    )

    if choice:
        selected_id = movie_map[choice] # pyright: ignore
        print(f"ID: {selected_id}")

        print(api.fetch_movie_metadata(selected_id))
    else:
        print("No movie selected.")

