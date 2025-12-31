from os import abort
import requests
from omdbapi.movie_search import GetMovie, GetMovieException
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
        self.omdb = GetMovie(api_key=self.api_key)

    def test_api_key(self, api_key: str) -> bool:
        """Test the validity of the API key"""
        try:
            # Create a new movie instance for testing
            GetMovie(api_key=api_key).get_movie(title='Interstellar')
            return True
        except GetMovieException:
            return False

    def fetch_movie_metadata(self, title: str) -> dict:
        """Fetch movie metadata using OMDB Api Endpoint"""
        try:
            self.movie = self.omdb.get_movie(title=title)
            # print(self.movie.items())
            return self.movie
        except GetMovieException as e:
            moai.says(f"[indian_red]x Sorry, Fetching movie error ({e}) occured.[/]")

            if e == "Movie not found!":
                console.print("You can check the title at [underline sky_blue2]https://www.omdb.org/en/us/search[/]")
            abort()

    def fetch_box_office_worldwide(self, imdbid: str):
        """Import the worldwide boxoffice"""
        from bs4 import BeautifulSoup
        url = f"https://www.boxofficemojo.com/title/{imdbid}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

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
            moai.says(f"[indian_red]x Sorry, Web Scrapping Error ({e}) occured.[/]")

    def fetch_poster(self):
        """Fetch movie poster and store in posters in data"""
        poster_link = self.movie['poster'] # pyright: ignore

        filename = poster_link.split("/")[-1].split("@")[0] + ".jpg"
        file_path = path.poster_dir / filename

        # check if the poster already exist
        if file_path.exists():
            moai.says(f"[yellow]Poster file already exist -> ([italic]No need to fetch a new one![/])[/]")
            return file_path
        else:
            try:
                response = requests.get(poster_link, stream=True, timeout=10)
                response.raise_for_status() # Check for 404/500 errors

                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                moai.says(f"[green]✓ Poster ({file_path}) [italic]saved[/italic] successfully[/]")
                return file_path

            except Exception as e:
                moai.says(f"[indian_red]x Sorry, Poster Error ({e}) occured.[/]")
                return

if __name__ == "__main__":
    print(MovieManager().fetch_box_office_worldwide("tt1877830"))
