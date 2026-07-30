from os import abort
import requests
from .api import API
from rich.console import Console

from .path import PathManager
from .moai import Moai
from .config import ConfigManager

path = PathManager()
console = Console()
config_manager = ConfigManager()
moai = Moai()

class MovieManager:
    """Manage any resources and data regarding movies"""
    def __init__(self) -> None:
        self.api_key = config_manager.get_config("API", "omdb_api_key")
        self.api = API(self.api_key)

    def test_api_key(self, api_key: str) -> bool:
        """Test the validity of the API key"""
        try:
            # Create a new API_KEY so not use the self key
            api = API(api_key)
            movie = api.fetch_movie_metadata("tt3896198", silent=True)
            if movie:
                return True
            else:
                return False
        except Exception:
            return False

    def fetch_movie_metadata(self, imdbid: str) -> dict:
        """Fetch movie metadata using OMDB Api Endpoint"""
        try:
            self.movie = self.api.fetch_movie_metadata(imdbid=imdbid)
            return self.movie
        except Exception as e:
            moai.says(f"[indian_red]x Sorry, Fetching movie error ({e}) occured.[/]", type="error")

            if e == "Movie not found!":
                console.print("You can check the title at [underline sky_blue2]https://www.omdb.org/en/us/search[/]")
            abort()

    def search_movie(self, title: str):
        """Search movies that have a close name"""
        try:
            return self.api.search_movie(title=title)
        except Exception as e:
            if str(e) == "'Movie not found!'":
                moai.says(
                    f"[indian_red]x Sorry, The movie could not be found![/]\n"
                    "          [dim]Try use imdbid:[/] [yellow]tt..[/]\n\n"
                    "If still not found..  [dim]v--search here--v[/]\n"
                    "      [underline sky_blue2]https://www.omdb.org/en/us/search[/]",
                    type="error"
                )
            else:
                console.print("hi")
            abort()

    def fetch_box_office_worldwide(self, imdbid: str):
        """Import the worldwide boxoffice"""
        from bs4 import BeautifulSoup
        url = f"https://www.boxofficemojo.com/title/{imdbid}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        with console.status("[bold]Searching Worldwide Boxoffice Data...", spinner="earth"):
            try:
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                money_spans = soup.find_all("span", class_="money")
                # On Box Office Mojo title pages:
                # Index 0 is usually Domestic, Index 1 is International, Index 2 is Worldwide
                if len(money_spans) >= 3:
                    return money_spans[2].text.strip()
                elif len(money_spans) > 0:
                    # If the movie only has one total, it might be the Worldwide/Domestic total
                    return money_spans[-1].text.strip()
                return None
            except Exception as e:
                moai.says(f"[indian_red]x Sorry, Web Scrapping Error ({e}) occured.[/]", type="error")

    def fetch_rt_data(self, title: str, year: str, tomato_url: str | None = None):
        """Fetch Rotten Tomatoes data by movie title and year"""
        from .rt import fetch_rotten_tomatoes_data
        debug = config_manager.get_config("UI", "debug").lower() == "true"
        with console.status("[bold]Fetching Rotten Tomatoes data...", spinner="earth"):
            try:
                if not tomato_url:
                    tomato_url = self._fetch_tomato_url(title, year, debug)
                return fetch_rotten_tomatoes_data(title, year, tomato_url=tomato_url, debug=debug)
            except Exception:
                return None

    def _fetch_tomato_url(self, title: str, year: str, debug: bool = False) -> str | None:
        """Use the omdb library to get the tomato_url from OMDB API"""
        import omdb
        from .rt import _debug_print
        omdb.set_default("apikey", self.api_key)
        _debug_print(f"Fetching tomato_url via omdb lib: title={title}, year={year}", debug)
        try:
            result = omdb.get(title=title, year=year, tomatoes=True)
            tomato_url = result.get("tomato_url") if isinstance(result, dict) else None
            _debug_print(f"omdb lib response type: {type(result)}", debug)
            _debug_print(f"omdb lib tomato_url: {tomato_url}", debug)
            if debug and isinstance(result, dict):
                tomato_keys = {k: v for k, v in result.items() if "tomato" in k}
                _debug_print(f"omdb lib tomato fields: {tomato_keys}", debug)
            return tomato_url
        except Exception as e:
            _debug_print(f"omdb lib error: {type(e).__name__}: {e}", debug)
            return None

    def fetch_poster(self):
        """Fetch movie poster and store in posters in data"""
        poster_link = self.movie['poster'] # pyright: ignore

        filename = poster_link.split("/")[-1].split("@")[0] + ".jpg"
        file_path = path.poster_dir / filename

        if file_path.exists():
            moai.says(f"[yellow]It seems like your poster already existed\n[dim]    So.. no need to fetch a new one![/dim][/]", type="nerd")
            return file_path

        try:
            response = requests.get(poster_link, stream=True, timeout=10)
            response.raise_for_status() 

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            moai.says(f"[green]✓ Poster saved successfully[/]", type="fun")
            return file_path

        except Exception:
            moai.says(
                f"[dim]We are very sorry because the [italic]poster link[/italic] is [indian_red]broken[/indian_red].. \n"
                "    You might need to change the poster [italic]manually[/italic]..[/]\n"
                "        Try.. [yellow]`mvw list` -> `Change Poster`[/yellow]",
                type="sad"
            )

if __name__ == "__main__":
    print(MovieManager().fetch_box_office_worldwide("tt1877830"))
