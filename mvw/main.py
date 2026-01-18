import typer
import click
from iterfzf import iterfzf
from rich.console import Console
from typing import Optional
from pathlib import Path

from .config import ConfigManager
from .display import DisplayManager
from .movie import MovieManager
from .database import DatabaseManager
from .moai import Moai
from .menu import MenuManager
from .path import PathManager

app = typer.Typer(help="MVW - CLI MoVie revieW", context_settings={"help_option_names" : ["-h", "--help"]})

config_manager = ConfigManager()
movie_manager = MovieManager()
database_manager = DatabaseManager()
moai = Moai()
console = Console()
menu = MenuManager()
path = PathManager()

@app.command()
def config(
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="Set OMDb API key"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Set your name as the reviewer"),
    theme: Optional[str] = typer.Option(None, "--theme", "-t", help="Set the color, OPTS:\n"
                                        "(gruvbox, catppuccin, nord)"
                                        ),
    poster_width: Optional[str] = typer.Option(None, "--poster-width", "-w", help="Set the poster width (default: 30)"),
    poster_border: Optional[bool] = typer.Option(None, "--border", "-b", help="Toggle the Poster border visibility", show_default=False),
    moai_says: Optional[bool] = typer.Option(None, "--moai", "-m", help="Toggle the Moai help", show_default=False),
    review: Optional[bool] = typer.Option(None, "--review", "-rv", help="Toggle the Review section", show_default=False),
    worldwide_boxoffice: Optional[bool] = typer.Option(None, "--worldwide-boxoffice", "-wb", help="Toggle the boxoffice scope (worldwide vs domestic)", show_default=False),
    hide_key: Optional[bool] = typer.Option(None, "--hide-key", "-hk", help="Hide the api key", show_default=False),
    reset: bool = typer.Option(False, "--reset", "-r", help="Reset the config into default configuration"),
):
    """Config the settings"""
    if reset:
        config_manager.reset_to_default_config()

    if api_key:
        # Check the api key validation
        if  movie_manager.test_api_key(api_key):
            config_manager.set_config("API", "omdb_api_key", api_key)
            moai.says(f"[green]✓ API Key [italic]added[/italic] successfully[/]")
        else:
            moai.says(f"[indian_red]x Sorry, API Key ({api_key}) seems [italic]wrong[/]")

    if name:
        config_manager.set_config("USER", "name", name)

    if moai_says:
        moai_bool = config_manager.get_config("UI", "moai").lower() == "true"

        if moai_bool:
            moai.says(f"[dim light_steel_blue3]Bye, see you again later..[/]")
            config_manager.set_config("UI", "moai", "false")
        else:
            config_manager.set_config("UI", "moai", "true")
            moai.says(f"[green]Hi, nice to see you again![/]")

    if review:
        review_bool = config_manager.get_config("UI", "review").lower() == "true"

        if review_bool:
            moai.says(f"[dim]The review will be hidden[/]")
            config_manager.set_config("UI", "review", "false")
        else:
            config_manager.set_config("UI", "moai", "true")
            moai.says(f"[green]The review will be [italic]un[/italic]hidden[/green]")

    if worldwide_boxoffice:
        worldwide_boxoffice_bool = config_manager.get_config("DATA", "worldwide_boxoffice").lower() == "true"
        if worldwide_boxoffice_bool:
            config_manager.set_config("DATA", "worldwide_boxoffice", "false")
            moai.says(f"[green]The boxoffice scope => [italic]domestic[/]")
        else:
            moai.says(f"[green]The boxoffice scope => [italic]worldwide[/]")
            config_manager.set_config("DATA", "worldwide_boxoffice", "true")

    if poster_width:
        try:
            int(poster_width)
            config_manager.set_config("UI", "poster_width", poster_width)
            moai.says(f"[green]✓ Poster width ({poster_width}) [italic]resized[/italic] successfully[/]")
        except:
            moai.says(f"[indian_red]x Sorry, Poster Width cannot be other than [italic]whole number[/]\n[dim]                    P/S: no comma[/]")

    if poster_border:
        poster_border_bool = config_manager.get_config("UI", "poster_border").lower() == "true"
        if poster_border_bool :
            config_manager.set_config("UI", "poster_border", "false")
            moai.says(f"[yellow]The poster border will be [italic]hidden[/]")
        else:
            moai.says(f"[green]The poster border will be [italic]shown[/]")
            config_manager.set_config("UI", "poster_border", "true")

    if hide_key:
        hide_key_bool = config_manager.get_config("UI", "hide_key").lower() == "true"
        if hide_key_bool:
            config_manager.set_config("UI", "hide_key", "false")
            moai.says(f"[yellow]The api key will be [italic]shown[/]")
        else:
            moai.says(f"[green]The api key will be [italic]hidden[/]")
            config_manager.set_config("UI", "hide_key", "true")

    if theme:
        config_manager.set_config("UI", "theme", theme)
        moai.says(f"[green]✓ The theme ({theme}) [italic]configured[/italic] successfully[/]")

    config_manager.show_config()

@app.command(hidden=True)
def edit(
    movie,
    poster_path: str = "",
    already_reviewed: bool = True
):
    """Edit the star and review"""
    if already_reviewed:
        display_manager = DisplayManager(movie, movie['poster_local_path'])
        display_manager.display_movie_info(movie['star'], movie['review'])

        moai.says(
            f"Seems like your past rating is {movie['star']}.\n"
            f"Press [yellow]ENTER[/] if want to skip it"
        )

        star = click.prompt(
            "MVW 󱓥 (0 ~ 5)",
            type=click.FloatRange(0, 5),
            default=movie['star'],
            show_default=True,
            prompt_suffix="> "
        )
        
        moai.says(
            f"Seems like you have already reviewed [yellow]\"{movie['title']}\"[/],\n"
            "I recommend for you to [cyan]re-edit[/] using your [italic]default text editor[/]\n"
            "so you won't need to write them from [indian_red italic]scratch..[/]"
        )

        use_text_editor = click.confirm(
            "MVW 󰭹  text editor",
            default=False,
            prompt_suffix="? ",
            show_default=True
        )
        if use_text_editor:
            review: str = click.edit(movie['review']) # pyright: ignore
        else:
            review = click.prompt("MVW 󰭹 ", prompt_suffix="> ")

        database_manager.update_star_review(movie['imdbid'], star, review) 
        moai.says(f"[green]✓ Your Star & Review got [italic]updated[/italic] successfully[/]")
        return star, review
    else:
        display_manager = DisplayManager(movie, poster_path)
        display_manager.display_movie_info()

        moai.says(
            "The rating can be half [cyan](x.5)[/], it will be shown as [yellow] [/]\n"
                "[dim]eg:[/] rating 2.5 =>[yellow]      [/] "
        )

        star = click.prompt(
            "MVW 󱓥 (0 ~ 5)",
            type=click.FloatRange(0, 5),
            default=2.5,
            show_default=True,
            prompt_suffix="> "
        )

        moai.says(
            "The review section [italic]supports[/] [medium_purple1]rich[/] format.\n"
            "You can learn more at [sky_blue2 underline]https://rich.readthedocs.io/en/stable/markup.html[/]\n"
            "[dim]>> Examples: \\[blue]This is blue\\[/blue] -> [blue]This is blue[/blue], + more[/dim]" # pyright: ignore
            "\n\nIn this section, you can choose to write the review [italic cyan]directly[/] in the terminal [default] (press [yellow]`ENTER`[/])\nor using your [italic hot_pink3]default text editor[/] [yellow](type `y`, `ENTER`)[/]"
        , moai="big")

        use_text_editor = click.confirm(
            "MVW 󰭹  text editor",
            default=False,
            show_default=True,
            prompt_suffix="? "
        )
        if use_text_editor:
            review: str = click.edit() # pyright: ignore
        else:
            moai.says(
                "Be [bold]careful[/] to not make as much mistake as you [indian_red]cannot[/] move to the left except [italic]backspacing[/]"
            )
            review = click.prompt("MVW 󰭹 ", prompt_suffix="> ")

        database_manager.store_movie_metadata(movie, poster_path, star, review) 
        return star, review

@app.command(hidden=True)
def save(movie, poster_local_path):
    """Save the movie display info"""
    DisplayManager(movie, poster_local_path).save_display_movie_info()

@app.command()
def interactive(title: str):
    """(DEFAULT) Search the movie title, star, edit, and save"""
    if config_manager.get_config("API", "omdb_api_key"):
        moai.title()
        moai.says("[yellow] [/]: If you do not see a [italic yellow]smile[/] icon, [cyan]nerdfont[/] is not installed. ", moai="no")
        moai.says(
            "Search Guide:\n"
            "* [cyan]movie[/]   [dim]# standard[/]\n"
            "* [cyan]imdbid[/]  [dim]# include 'tt'[/]"
        )

        if not title:
            title = click.prompt("MVW  ", prompt_suffix="> ")

        search_response = movie_manager.search_movie(title)

        try:
            search_movies_list = search_response.get('search', [])

            search_movie_map = {f"{m['Title']} ({m['Year']})": m['imdbID'] for m in search_movies_list}

            choice = iterfzf(
                search_movie_map.keys()
            )

            if choice:
                selected_id = search_movie_map[choice] # pyright: ignore
            else:
                moai.says("It seems like you did not choose any movie")
        except AttributeError:
            selected_id = search_response['imdbid']

        movie: dict = movie_manager.fetch_movie_metadata(imdbid=selected_id)
        poster_path = movie_manager.fetch_poster()

        if poster_path == None:
            poster_path = "N/A"
        else:
            poster_path = str(poster_path.resolve())

        movie_already_reviewed = database_manager.get_movie_metadata_by_title(movie['title'])
        already_reviewed = False

        if movie_already_reviewed:
            movie = movie_already_reviewed
            already_reviewed = True

        star_review = edit(movie, poster_path, already_reviewed)

        moai.says("Do you want to have an [cyan]\"image\"[/] of your review?\nTo change theme, try [yellow]`mvw config -t <THEME>`[/]")
        screenshot = click.confirm(
            "MVW   (.svg)",
            default=False,
            prompt_suffix="? ",
            show_default=True
        )

        if screenshot:
            save(movie, poster_path)
        else:
            DisplayManager(movie, poster_path).display_movie_info(star_review[0], star_review[1])
    else:
        moai.says("Hi, [bold]API key[/] [indian_red]did not found[/], try [italic yellow]`mvw config --help`[/]\n"
                    "While doing that, you can apply Free API key here:\n"
                    "       [sky_blue2 underline]http://www.omdbapi.com/apikey.aspx[/]\n"
                    "             [dim]Try CTRL+left_click ^[/]", moai="big")

@app.command()
def list():
    """List all the reviewed movies"""
    all_reviewed_movies = database_manager.get_all_movies()

    movie_map = {movie['title']: movie for movie in all_reviewed_movies}

    selected_title = iterfzf(
        movie_map.keys(),
        preview="mvw preview -t {}",
        ansi=True,
        multi=False
    )

    if selected_title:
        metadata = movie_map.get(selected_title)
        imdbid: str = str(metadata.get('imdbid'))

        movie = database_manager.get_movie_metadata_by_imdbid(imdbid)

        menu.add_feature("Preview", preview, imdbid=imdbid)
        menu.add_feature("Delete", delete, imdbid=imdbid)
        menu.add_feature("Edit", edit, movie=movie, poster_path=movie['poster_local_path'], already_reviewed=True)
        menu.add_feature("Save", save, movie=movie, poster_local_path=movie['poster_local_path'])
        menu.add_feature("Change Poster", poster, poster_path="", imdbid=imdbid)

        menu.run(imdbid=imdbid)

@app.command()
def poster(
    poster_path: Optional[str] = typer.Option("", "--path", "-p", help="The file path of the poster"),
    imdbid: Optional[str] = typer.Option(None, "--id", "-i", help="Change the poster for movie with tmdbid (tt..)"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Change the poster for movie with title (for now, need the exact title like in the review (case-sensitive))"),
):
    """Change the poster for movies"""
    if not (imdbid or title):
        moai.says("Choose either [cyan]id[/] or [indian_red]title[/], try [yellow]`poster -h`[/]")
        return

    attribute = "poster_local_path"
    print(poster_path)
    
    if poster_path == "":
        new_poster_path = path.image_picker()
    else:
        new_poster_path = poster_path

    if not Path(str(new_poster_path)).exists():
        moai.says(
            f"[indian_red]x Sorry, ({new_poster_path}) is [italic]not exist.[/]"
        )
        return

    if path.valid_image_path(str(new_poster_path)):
        if imdbid:
            preview(imdbid=imdbid, poster_path=str(new_poster_path))
            change = click.confirm(
                "MVW  change",
                default=True,
                prompt_suffix="? ",
                show_default=True
            )
            if change:
                database_manager.set_key_value(imdbid, attribute, new_poster_path)
            else:
                moai.says(f"[yellow]✓ Poster ({imdbid}) [italic]remain[/italic] as usual.[/]")
                preview(imdbid=imdbid)
        elif title:
            preview(title=title, poster_path=str(new_poster_path))
            change = click.confirm(
                "MVW  change",
                default=True,
                prompt_suffix="? ",
                show_default=True
            )
            if change:
                database_manager.set_key_value(title, attribute, new_poster_path)
            else:
                moai.says(f"[yellow]✓ Poster ({imdbid}) [italic]remain[/italic] as usual.[/]")
                preview(title=title)
    else:
        moai.says(
            f"[indian_red]x Sorry, ({poster_path}) is [italic]unsupported.[/][/]\n"
                "[dim]Supported: .jpg, .jpeg, .png, .webp[/]"
        )
        return

@app.command()
def preview(
    poster_path: str = "",
    imdbid: Optional[str] = typer.Option(None, "--id", "-i", help="Preview the review using tmdbid (tt..)"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Preview the review using title (for now, need the exact title like in the review (case-sensitive))"),
):
    """Preview reviewed movies"""
    if not (imdbid or title):
        moai.says("Choose either to preview using [cyan]id[/] or [indian_red]title[/], try [yellow]`preview -h`[/]")
        return

    if imdbid:
        previewed_movie = database_manager.get_movie_metadata_by_imdbid(imdbid)
    elif title:
        previewed_movie = database_manager.get_movie_metadata_by_title(title)

    print(poster_path)
    if poster_path == "":
        display_manager = DisplayManager(previewed_movie, previewed_movie['poster_local_path'])
        display_manager.display_movie_info(previewed_movie['star'],previewed_movie['review'])
    else:
        display_manager = DisplayManager(previewed_movie, poster_path)
        display_manager.display_movie_info(previewed_movie['star'],previewed_movie['review'])

@app.command()
def delete(
    imdbid: Optional[str] = typer.Option(None, "--id", "-i", help="Delete the review movie using tmdbid (tt..)"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Delete the review movie using title (for now, need the exact title like in the review (case-sensitive))"),
):
    """Delete reviewed movies"""
    if not (imdbid or title):
        moai.says("Choose either to delete using [cyan]id[/] or [indian_red]title[/], try [yellow]`delete -h`[/]")
        return

    if imdbid:
        preview(imdbid=imdbid, title=None, poster_path="")
        moai.says("Your movie were found! Are you sure, you want to delete the movie?")
        delete = click.confirm(
            "MVW  delete",
            default=True,
            prompt_suffix="? ",
            show_default=True
        )
        if delete:
            database_manager.delete_movie_entry_by_id(imdbid)
    elif title:
        preview(imdbid=None, title=title, poster_path="")
        moai.says("Your movie were [green]found![/] But.. Are you sure, you want to [italic red]delete[/] the movie?")
        delete = click.confirm(
            "MVW  delete",
            default=True,
            prompt_suffix="? ",
            show_default=True
        )
        if delete:
            database_manager.delete_movie_entry_by_title(title)

# Default to interactive
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        interactive("")

if __name__ == "__main__":
    app()
