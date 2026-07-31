import sys
import typer
import click
from iterfzf import iterfzf
from rich.console import Console
from typing import Optional
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from .config import ConfigManager
from .display import DisplayManager
from .movie import MovieManager
from .database import DatabaseManager
from .moai import Moai
from .menu import MenuManager
from .path import PathManager

app = typer.Typer(
    help="MVW - CLI MoVie revieW",
    context_settings={"help_option_names": ["-h", "--help"]},
)

config_manager = ConfigManager()
movie_manager = MovieManager()
database_manager = DatabaseManager()
moai = Moai()
console = Console()
menu = MenuManager()
path = PathManager()


@app.command()
def config(
    api_key: Optional[str] = typer.Option(
        None, "--api-key", "-k", help="Set OMDb API key"
    ),
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Set your name as the reviewer"
    ),
    theme: Optional[str] = typer.Option(
        None, "--theme", "-t", help="Set the color, OPTS:\n(gruvbox, catppuccin, nord)"
    ),
    poster_width: Optional[str] = typer.Option(
        None, "--poster-width", "-w", help="Set the poster width (default: 30)"
    ),
    poster_border: Optional[bool] = typer.Option(
        None,
        "--border",
        "-b",
        help="Toggle the Poster border visibility",
        show_default=False,
    ),
    moai_says: Optional[bool] = typer.Option(
        None, "--moai", "-m", help="Toggle the Moai help", show_default=False
    ),
    review: Optional[bool] = typer.Option(
        None, "--review", "-rv", help="Toggle the Review section", show_default=False
    ),
    worldwide_boxoffice: Optional[bool] = typer.Option(
        None,
        "--worldwide-boxoffice",
        "-wb",
        help="Toggle the boxoffice scope (worldwide vs domestic)",
        show_default=False,
    ),
    hide_key: Optional[bool] = typer.Option(
        None, "--hide-key", "-hk", help="Hide the api key", show_default=False
    ),
    render: Optional[str] = typer.Option(
        None, "--render", "-r", help="Set render style (pixel, block, ascii)"
    ),
    reset: bool = typer.Option(
        False, "--reset", "-R", help="Reset the config into default configuration"
    ),
    charset: Optional[str] = typer.Option(
        None, "--charset", "-c", help="Set ASCII charset (minimal, dots, blocks) for ascii renderer"
        ),
    debug: Optional[bool] = typer.Option(
        None, "--debug", "-d", help="Toggle debug mode for RT scraping", show_default=False
        ),
):
    """Config the settings"""
    if reset:
        config_manager.reset_to_default_config()

    if api_key:
        # Check the api key validation
        if movie_manager.test_api_key(api_key):
            config_manager.set_config("API", "omdb_api_key", api_key)
            moai.says(
                f"[green]✓ API Key [italic]added[/italic] successfully[/]", type="fun"
            )
        else:
            moai.says(
                f"[yellow]x Ermm.. actually the API Key ({api_key}) is [italic]invalid~[/]\n[dim]          Double check pls, Thank you[/]",
                type="nerd",
            )

    if name:
        config_manager.set_config("USER", "name", name)

    if moai_says:
        moai_bool = config_manager.get_config("UI", "moai").lower() == "true"

        if moai_bool:
            moai.says(
                f"[dim light_steel_blue3]Bye, see you again later..[/]", type="sad"
            )
            config_manager.set_config("UI", "moai", "false")
        else:
            config_manager.set_config("UI", "moai", "true")
            moai.says(f"[green]Hi, nice to see you again![/]", type="fun")

    if review:
        review_bool = config_manager.get_config("UI", "review").lower() == "true"

        if review_bool:
            moai.says(f"[dim]The review will be hidden[/]", type="sad")
            config_manager.set_config("UI", "review", "false")
        else:
            config_manager.set_config("UI", "review", "true")
            moai.says(
                f"[green]The review will be [italic]un[/italic]hidden[/green]",
                type="fun",
            )

    if worldwide_boxoffice:
        worldwide_boxoffice_bool = (
            config_manager.get_config("DATA", "worldwide_boxoffice").lower() == "true"
        )
        if worldwide_boxoffice_bool:
            config_manager.set_config("DATA", "worldwide_boxoffice", "false")
            moai.says(f"[green]The boxoffice scope => [italic]domestic[/]", type="fun")
        else:
            moai.says(f"[green]The boxoffice scope => [italic]worldwide[/]", type="fun")
            config_manager.set_config("DATA", "worldwide_boxoffice", "true")

    if poster_width:
        try:
            int(poster_width)
            config_manager.set_config("UI", "poster_width", poster_width)
            moai.says(
                f"[green]✓ Poster width ({poster_width}) [italic]resized[/italic] successfully[/]",
                type="fun",
            )
        except:
            moai.says(
                f"[yellow]x Based on my calculation, [bold]Poster Width[/bold] cannot be other than a [italic]whole number[/]\n[dim]                   P/S: no comma, fraction or decimal[/]",
                type="nerd",
            )

    if poster_border:
        poster_border_bool = (
            config_manager.get_config("UI", "poster_border").lower() == "true"
        )
        if poster_border_bool:
            config_manager.set_config("UI", "poster_border", "false")
            moai.says(f"[green]The poster border will be [italic]hidden[/]", type="fun")
        else:
            moai.says(f"[green]The poster border will be [italic]shown[/]", type="fun")
            config_manager.set_config("UI", "poster_border", "true")

    if hide_key:
        hide_key_bool = config_manager.get_config("UI", "hide_key").lower() == "true"
        if hide_key_bool:
            config_manager.set_config("UI", "hide_key", "false")
            moai.says(
                f"[yellow]The api key will be [italic]shown[/italic],\n[dim]P/S: Remember don't share your key with anyone[/]",
                type="nerd",
            )
        else:
            moai.says(f"[green]The api key will be [italic]hidden[/]", type="fun")
            config_manager.set_config("UI", "hide_key", "true")

    if theme:
        config_manager.set_config("UI", "theme", theme)
        moai.says(
            f"[green]✓ The theme ({theme}) [italic]configured[/italic] successfully[/]",
            type="fun",
        )

    if render:
        from .renderers import RendererRegistry

        available_renderers = RendererRegistry.list_renderers()
        if render in available_renderers:
            config_manager.set_config("UI", "render", render)
            moai.says(
                f"[green]✓ The render style ({render}) [italic]configured[/italic] successfully[/]",
                type="fun",
            )
        else:
            moai.says(
                f"[yellow]x Sorry, '{render}' is not a valid render style.\n[dim]Available options: {', '.join(available_renderers)}[/]",
                type="nerd",
            )

    if charset:
        valid_charsets = ["minimal", "dots", "blocks"]
        if charset in valid_charsets:
            config_manager.set_config("UI", "charset", charset)
            moai.says(
                  f"[green]✓ The charset ({charset}) [italic]configured[/italic] successfully[/]",
                  type="fun",
              )
        else:
          moai.says(
              f"[yellow]x Sorry, '{charset}' is not a valid charset.\n[dim]Available options: {', '.join(valid_charsets)}[/]",
              type="nerd",
          )

    if debug:
        debug_bool = config_manager.get_config("UI", "debug").lower() == "true"
        if debug_bool:
            config_manager.set_config("UI", "debug", "false")
            moai.says(f"[green]Debug mode [italic]disabled[/]", type="fun")
        else:
            config_manager.set_config("UI", "debug", "true")
            moai.says(f"[yellow]Debug mode [italic]enabled[/]", type="nerd")

    config_manager.show_config()


@app.command(hidden=True)
def edit(movie, poster_path: str = "", already_reviewed: bool = True):
    """Edit the star and review"""
    if already_reviewed:
        if not movie.get("rt_tomatometer"):
            rt_data = movie_manager.fetch_rt_data(
                movie["title"], movie["year"],
                tomato_url=movie.get("tomato_url")
            )
            if rt_data and rt_data.get("rt_tomatometer") is not None:
                movie.update(rt_data)
                database_manager.set_rt_scores(movie["imdbid"], rt_data)

        display_manager = DisplayManager(movie, movie["poster_local_path"])
        display_manager.display_movie_info(movie["star"], movie["review"])

        moai.says(
            f"[yellow]It seems like your past rating is {movie['star']}.\n"
            f"    [dim]Press [bold]ENTER[/bold] if want to skip it[/]",
            type="nerd",
        )

        star = click.prompt(
            "MVW 󱓥 (0 ~ 5)",
            type=click.FloatRange(0, 5),
            default=movie["star"],
            show_default=True,
            prompt_suffix="> ",
        )

        moai.says(
            f'You already reviewed [yellow]"{movie["title"]}"[/],\n'
            "I recommend for you to [cyan]re-edit[/] using your [italic]default text editor[/]\n"
            "so you won't need to write them from [indian_red italic]scratch..[bold] again..[/]",
            type="info",
        )

        use_text_editor = click.confirm(
            "MVW 󰭹  text editor", default=True, prompt_suffix="? ", show_default=True
        )
        if use_text_editor:
            review: str = click.edit(movie["review"])  # pyright: ignore
        else:
            review = click.prompt("MVW 󰭹 ", prompt_suffix="> ")

        database_manager.update_star_review(movie["imdbid"], star, review)
        moai.says(
            f"[green]✓ Your Star & Review got [italic]updated[/italic] successfully[/]",
            type="fun",
        )
        return star, review
    else:
        display_manager = DisplayManager(movie, poster_path)
        display_manager.display_movie_info()

        moai.says(
            "[yellow]Did you know that, MVW support half rating [bold](x.5)[/bold], it will be shown as  \n"
            "                    [dim]eg:[/dim] rating 2.5 =>      [/] ",
            type="nerd",
        )

        star = click.prompt(
            "MVW 󱓥 (0 ~ 5)",
            type=click.FloatRange(0, 5),
            default=2.5,
            show_default=True,
            prompt_suffix="> ",
        )

        moai.says(
            "The review section [italic]supports[/] [medium_purple1]rich[/] format.\n"
            "You can learn more at [sky_blue2 underline]https://rich.readthedocs.io/en/stable/markup.html[/]\n"
            "[dim]>> Examples: \\[cyan]This is blue\\[/cyan] -> [cyan]This is blue[/cyan], + more[/dim]"  # pyright: ignore
            "\n\nIn this section, you can choose to write the review [italic cyan]directly[/] in the terminal [default] (press [yellow]`ENTER`[/])\nor using your [italic cyan]default text editor[/] [yellow](type `y`, `ENTER`)[/]",
            type="info",
        )

        use_text_editor = click.confirm(
            "MVW 󰭹  text editor", default=False, show_default=True, prompt_suffix="? "
        )
        if use_text_editor:
            review: str = click.edit()  # pyright: ignore
        else:
            moai.says(
                "[dim]Be [bold]careful[/] to not make as much mistake as you [indian_red]cannot[/indian_red] move to the left except [italic]backspacing[/italic]\n"
                "                               [italic]I learned it the hard way[/]...[/]",
                type="sad",
            )
            review = click.prompt("MVW 󰭹 ", prompt_suffix="> ")
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
        moai.says(
            "[yellow] [/]: If you do not see a [italic yellow]smile[/] icon, [cyan]nerdfont[/] is not installed. ",
            moai="no",
        )
        moai.says(
            "Search Guide:\n"
            "* [cyan]movie[/]   [dim]# standard[/]\n"
            "* [cyan]imdbid[/]  [dim]# include 'tt'[/]",
            type="info",
        )

        if not title:
            title = click.prompt("MVW  ", prompt_suffix="> ")

        search_response = movie_manager.search_movie(title)

        try:
            search_movies_list = search_response.get("search", [])

            search_movie_map = {
                f"{m['Title']} ({m['Year']})": m["imdbID"] for m in search_movies_list
            }

            choice = iterfzf(search_movie_map.keys())

            if choice:
                selected_id = search_movie_map[choice]  # pyright: ignore
            else:
                moai.says(
                    "[yellow]It seems like you did not choose any movie[/]", type="nerd"
                )
        except AttributeError:
            selected_id = search_response["imdbid"]

        movie: dict = movie_manager.fetch_movie_metadata(imdbid=selected_id)
        poster_path = movie_manager.fetch_poster()

        rt_data = movie_manager.fetch_rt_data(
            movie['title'], movie['year'],
            tomato_url=movie.get('tomato_url')
        )
        if rt_data and rt_data.get("rt_tomatometer") is not None:
            movie.update(rt_data)
            from .rt import normalize_review_count
            critic_fmt = normalize_review_count(rt_data.get("rt_critic_reviews"))
            audience_fmt = normalize_review_count(rt_data.get("rt_audience_reviews"))
            moai.says(
                f"[hot_pink2]✓ I just searched (rottentomatoes.com) and found the RT scores "
                f"->  [bold]{rt_data['rt_tomatometer']}% ({critic_fmt})[/bold], "
                f"󰐢 [bold]{rt_data['rt_audience_score']}% ({audience_fmt})[/bold]\n"
                f"               ref: [cyan3 underline]{rt_data.get('tomato_url', movie.get('tomato_url', 'https://www.rottentomatoes.com/m/' + movie['title'].lower().replace(' ', '_')))}[/]",
                type="rt"
            )

        if poster_path == None:
            poster_path = "N/A"
        else:
            poster_path = str(poster_path.resolve())

        movie_already_reviewed = database_manager.get_movie_metadata_by_title(
            movie["title"]
        )
        already_reviewed = False

        if movie_already_reviewed:
            movie = movie_already_reviewed
            if rt_data and rt_data.get("rt_tomatometer") is not None:
                movie.update(rt_data)
            already_reviewed = True

        star_review = edit(movie, poster_path, already_reviewed)

        # Get the latest update (incase worldwide boxoffice)
        database_manager.store_movie_metadata(
            movie, poster_path, star=star_review[0], review=star_review[1]
        )

        moai.says(
            'Do you want to have an [cyan]"image"[/] of your review?\nP/S: To change the theme, try [yellow]`mvw config -t <THEME>`[/]',
            type="info",
        )
        screenshot = click.confirm(
            "MVW   (.svg)", default=False, prompt_suffix="? ", show_default=True
        )

        if screenshot:
            save(movie, poster_path)
        else:
            DisplayManager(movie, poster_path).display_movie_info(
                star_review[0], star_review[1]
            )
    else:
        moai.says(
            "Hi, I could [indian_red]not found[/] your [bold]API key[/], try [italic yellow]`mvw config --help`[/]\n"
            "While doing that, you can apply Free API key here:\n"
            "       [sky_blue2 underline]http://www.omdbapi.com/apikey.aspx[/]\n"
            "             [dim]Try CTRL+left_click ^[/]",
            type="info",
        )


@app.command()
def list():
    """List all the reviewed movies"""
    all_reviewed_movies = database_manager.get_all_movies()

    movie_map = {f"[{movie['imdbid']}] {movie['title']}": movie for movie in all_reviewed_movies}

    for movie in all_reviewed_movies:
        cache_file = path.cache_dir / f"{movie['imdbid']}.txt"
        if not cache_file.exists():
            database_manager._generate_preview_cache(movie)

    preview_cmd = f'"{sys.executable}" -m mvw._preview_helper "{path.cache_dir}" {{}}'

    selected_title = iterfzf(
        movie_map.keys(), preview=preview_cmd, ansi=True, multi=False
    )

    if selected_title:
        metadata = movie_map.get(selected_title)
        imdbid: str = str(metadata.get("imdbid"))

        movie = database_manager.get_movie_metadata_by_imdbid(imdbid)

        menu.add_feature("Preview", preview, imdbid=imdbid)
        menu.add_feature("Delete", delete, imdbid=imdbid)
        menu.add_feature(
            "Edit",
            edit,
            movie=movie,
            poster_path=movie["poster_local_path"],
            already_reviewed=True,
        )
        menu.add_feature(
            "Save", save, movie=movie, poster_local_path=movie["poster_local_path"]
        )
        menu.add_feature("Change Poster", poster, poster_path="", imdbid=imdbid)
        menu.add_feature("Fetch RT", fetch_rt, imdbid=imdbid)
        menu.add_feature("Refresh", refresh, imdbid=imdbid)

        menu_preview_cmd = f'"{sys.executable}" -m mvw._preview_helper "{path.cache_dir}" "{imdbid}"'
        menu.run(imdbid=imdbid, preview_cmd=menu_preview_cmd)


@app.command()
def poster(
    poster_path: Optional[str] = typer.Option(
        "", "--path", "-p", help="The file path of the poster"
    ),
    imdbid: Optional[str] = typer.Option(
        None, "--id", "-i", help="Change the poster for movie with tmdbid (tt..)"
    ),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        "-t",
        help="Change the poster for movie with title (for now, need the exact title like in the review (case-sensitive))",
    ),
):
    """Change the poster for movies"""
    if not (imdbid or title):
        moai.says(
            "Choose either [cyan]id[/] or [indian_red]title[/], try [yellow]`poster -h`[/]",
            type="info",
        )
        return

    attribute = "poster_local_path"
    print(poster_path)

    if poster_path == "":
        new_poster_path = path.image_picker()
    else:
        new_poster_path = poster_path

    if not Path(str(new_poster_path)).exists():
        moai.says(
            f"[indian_red]x Sorry, ({new_poster_path}) is [italic]not exist.[/]",
            type="error",
        )
        return

    if path.valid_image_path(str(new_poster_path)):
        if imdbid:
            preview(imdbid=imdbid, poster_path=str(new_poster_path))
            change = click.confirm(
                "MVW  change", default=True, prompt_suffix="? ", show_default=True
            )
            if change:
                database_manager.set_key_value(imdbid, attribute, new_poster_path)
            else:
                moai.says(
                    f"[yellow]✓ Don't worry, your poster ({imdbid}) [italic]remain[/italic] as before.[/]",
                    type="nerd",
                )
                preview(imdbid=imdbid)
        elif title:
            preview(title=title, poster_path=str(new_poster_path))
            change = click.confirm(
                "MVW  change", default=True, prompt_suffix="? ", show_default=True
            )
            if change:
                database_manager.set_key_value(title, attribute, new_poster_path)
            else:
                moai.says(
                    f"[yellow]✓ Don't worry, your poster ({title}) [italic]remain[/italic] as before.[/]",
                    type="nerd",
                )
                preview(title=title)
    else:
        moai.says(
            f"[indian_red]x Ermm.. actually ({poster_path}) format is [italic]unsupported.[/][/]\n"
            "          [dim]MVW only supports: .jpg, .jpeg, .png, .webp[/]",
            type="nerd",
        )
        return


@app.command()
def preview(
    poster_path: str = "",
    imdbid: Optional[str] = typer.Option(
        None, "--id", "-i", help="Preview the review using tmdbid (tt..)"
    ),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        "-t",
        help="Preview the review using title (for now, need the exact title like in the review (case-sensitive))",
    ),
):
    """Preview reviewed movies"""
    if not (imdbid or title):
        moai.says(
            "Choose either to preview using [cyan]id[/] or [indian_red]title[/], try [yellow]`preview -h`[/]",
            type="info",
        )
        return

    if imdbid:
        previewed_movie = database_manager.get_movie_metadata_by_imdbid(imdbid)
    elif title:
        previewed_movie = database_manager.get_movie_metadata_by_title(title)

    if previewed_movie and not previewed_movie.get("rt_tomatometer"):
        rt_data = movie_manager.fetch_rt_data(
            previewed_movie["title"], previewed_movie["year"],
            tomato_url=previewed_movie.get("tomato_url")
        )
        if rt_data and rt_data.get("rt_tomatometer") is not None:
            previewed_movie.update(rt_data)
            database_manager.set_rt_scores(previewed_movie["imdbid"], rt_data)

    print(poster_path)
    if poster_path == "":
        display_manager = DisplayManager(
            previewed_movie, previewed_movie["poster_local_path"]
        )
        display_manager.display_movie_info(
            previewed_movie["star"], previewed_movie["review"]
        )
    else:
        display_manager = DisplayManager(previewed_movie, poster_path)
        display_manager.display_movie_info(
            previewed_movie["star"], previewed_movie["review"]
        )


@app.command(hidden=True)
def fetch_rt(
    imdbid: Optional[str] = typer.Option(
        None, "--id", "-i", help="Fetch RT data for movie with imdbid (tt..)"
    ),
):
    """Manually provide a Rotten Tomatoes URL to fetch scores"""
    if not imdbid:
        return
    movie = database_manager.get_movie_metadata_by_imdbid(imdbid)
    if not movie:
        moai.says(f"[indian_red]x Movie not found[/]", type="error")
        return
    
    moai.says(
        f"[hot_pink2]Paste the Rotten Tomatoes URL for {movie['title']} ({movie['year']})[/]\n"
        "[dim]>> Examples: https://www.rottentomatoes.com/m/...",
        type="rt"
    )
    tomato_url = click.prompt("MVW  ", prompt_suffix="> ")
    
    if not tomato_url:
        return
    with console.status("[bold]Fetching Rotten Tomatoes data...", spinner="earth"):
        rt_data = movie_manager.fetch_rt_data(
            movie["title"], movie["year"], tomato_url=tomato_url
        )
    if rt_data and rt_data.get("rt_tomatometer") is not None:
        database_manager.set_rt_scores(imdbid, rt_data)
        preview(imdbid=imdbid)
    else:
        moai.says(
            f"[indian_red]x Could not extract RT scores from that URL[/]",
            type="error"
        )


@app.command(hidden=True)
def refresh(
    imdbid: Optional[str] = typer.Option(
        None, "--id", "-i", help="Refresh movie data for imdbid (tt..)"
    ),
):
    """Re-fetch all data from OMDB, RT, and box office"""
    if not imdbid:
        return
    existing = database_manager.get_movie_metadata_by_imdbid(imdbid)
    if not existing:
        moai.says(f"[indian_red]x Movie not found[/]", type="error")
        return
    fresh = movie_manager.fetch_movie_metadata(imdbid)
    if not fresh:
        return

    worldwide_bo = ConfigManager().get_config("DATA", "worldwide_boxoffice").lower() == "true"

    omdb_map = [
        ("title", "title"), ("year", "year"), ("rated", "rated"),
        ("released", "released"), ("runtime", "runtime"), ("genre", "genre"),
        ("director", "director"), ("writer", "writer"), ("actors", "actors"),
        ("plot", "plot"), ("language", "language"), ("country", "country"),
        ("awards", "awards"), ("metascore", "metascore"),
        ("imdbrating", "imdbrating"), ("imdbvotes", "imdbvotes"),
        ("production", "production"),
        ("website", "website"), ("dvd", "dvd"), ("type", "type"),
        ("poster_link", "poster"),
    ]
    if not worldwide_bo:
        omdb_map.append(("boxoffice", "boxoffice"))
    for db_col, omdb_key in omdb_map:
        new_val = fresh.get(omdb_key)
        old_val = existing.get(db_col)
        if new_val is not None and str(new_val) != str(old_val):
            database_manager.set_key_value(imdbid, db_col, new_val)

    with console.status("[bold]Fetching Rotten Tomatoes data...", spinner="earth"):
        rt_data = movie_manager.fetch_rt_data(
            fresh.get("title", existing["title"]),
            fresh.get("year", existing["year"]),
            tomato_url=existing.get("tomato_url") or fresh.get("tomato_url"),
        )
    if rt_data and rt_data.get("rt_tomatometer") is not None:
        for key in ("rt_tomatometer", "rt_audience_score", "rt_certification", "rt_critic_reviews", "rt_audience_reviews"):
            new_val = rt_data[key]
            old_val = existing.get(key)
            if new_val is not None and str(new_val) != str(old_val):
                database_manager.set_key_value(imdbid, key, new_val)
        from .rt import normalize_review_count
        critic_fmt = normalize_review_count(rt_data.get("rt_critic_reviews"))
        audience_fmt = normalize_review_count(rt_data.get("rt_audience_reviews"))
        moai.says(
            f"[hot_pink2]✓ I just searched (rottentomatoes.com) and found the RT scores "
            f"->  [bold]{rt_data['rt_tomatometer']}% ({critic_fmt})[/bold], "
            f"󰐢 [bold]{rt_data['rt_audience_score']}% ({audience_fmt})[/bold]\n"
            f"               ref: [cyan3 underline]{rt_data.get('tomato_url', existing.get('tomato_url', 'https://www.rottentomatoes.com/m/' + existing['title'].lower().replace(' ', '_')))}[/]",
            type="rt"
        )

    if worldwide_bo:
        database_manager.set_movie_boxoffice_to_worldwide(imdbid)

    moai.says(f"[sky_blue1]✓ Refresh complete for {existing['title']}[/]", type="info")
    preview(imdbid=imdbid)


@app.command()
def delete(
    imdbid: Optional[str] = typer.Option(
        None, "--id", "-i", help="Delete the review movie using tmdbid (tt..)"
    ),
    title: Optional[str] = typer.Option(
        None,
        "--title",
        "-t",
        help="Delete the review movie using title (for now, need the exact title like in the review (case-sensitive))",
    ),
):
    """Delete reviewed movies"""
    if not (imdbid or title):
        moai.says(
            "Choose either to delete using [cyan]id[/] or [indian_red]title[/], try [yellow]`delete -h`[/]",
            type="info",
        )
        return

    if imdbid:
        preview(imdbid=imdbid, title=None, poster_path="")
        moai.says(
            "               [dim]We found your movie..\nBut.. Are you sure, you want to [italic red]delete[/] the movie?",
            type="sad",
        )
        delete = click.confirm(
            "MVW  delete", default=True, prompt_suffix="? ", show_default=True
        )
        if delete:
            database_manager.delete_movie_entry_by_id(imdbid)
    elif title:
        preview(imdbid=None, title=title, poster_path="")
        moai.says(
            "               [dim]We found your movie\nBut.. Are you sure, you want to [italic red]delete[/] the movie?",
            type="sad",
        )
        delete = click.confirm(
            "MVW  delete", default=True, prompt_suffix="? ", show_default=True
        )
        if delete:
            database_manager.delete_movie_entry_by_title(title)


# Default to interactive
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        interactive("")


def main_run():
    """Entry point for the mvw CLI with graceful interrupt handling"""
    try:
        code = app(standalone_mode=False)
        if code:
            raise SystemExit(code)
    except KeyboardInterrupt:
        # add a new line before the goodbye message
        print()
        moai.says("[dim]Goodbye, see you again later..[/]", type="sad")
    except click.exceptions.Abort:
        print()
        moai.says("[dim]Goodbye, see you again later..[/]", type="sad")
    except click.exceptions.ClickException as e:
        e.show()
        raise SystemExit(e.exit_code)


if __name__ == "__main__":
    main_run()
