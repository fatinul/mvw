<div align="center">
<table>
  <tr>
    <td valign="center">
<pre>
   __  ______  __      ___     __
  /  |/  /| | / /      | | /| / /
 / /|_/ / | |/ /       | |/ |/ / 
/_/  /_/o |___/ie revie|__/|__/ 
</pre>
    </td>
    <td valign="center">
      <h3>Fastfetch inspired movie reviews</h3>
      <p><em>Catalogue your own movie review inside your terminal.</em></p>
      <img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python">
      <img src="https://img.shields.io/github/license/fatinul/mvw" alt="License">
      <img alt="GitHub Release" src="https://img.shields.io/github/v/release/fatinul/mvw?color=green">
      <br><br>
      <code>pipx install mvw</code>
      <br><br>
    </td>
  </tr>
</table>
</div>


---

<img src="https://raw.githubusercontent.com/fatinul/mvw/main/images/welcome.png" align="center">

```
  ▁▁     ╭─────────────────────────────────────╮
 ▁▁▁│    │ These are some demos when using MVW │
┌┘└ ░▌   ╰─────────────────────────────────────╯
╚═══╝    F: Psst.. his name is MOAI (nice to meet u)                                     
```
### Interactive
Default usage where you will get to experience the full experience of MVW. You will get to search, rate, review and also save your review. Every reviews will be saved in your local machine!

![Interactive Command](https://raw.githubusercontent.com/fatinul/mvw/main/demos/demo-interactive.gif)

### List
You will get to see every past reviews that you had done in a simple interface supported by [iterfzf](https://github.com/dahlia/iterfzf)) which uses the "__Fuzzy Search__"

![List Command](https://raw.githubusercontent.com/fatinul/mvw/main/demos/demo-list.gif)

### Config
Everything that you can see in the config list can be configurable. From the poster_width, theme, your name, and even worldwide-boxoffice feature

![Config Command](https://raw.githubusercontent.com/fatinul/mvw/main/demos/demo-config.gif)

### Theme

> NOTE: Most modern browser supports nerdfont icons in `svg`, you just need to _choose_ nerdfont as **default** in the settings.
> You can see `svg` below if it is _supported_.

- Gruvbox (The Default Theme)
![Gruvbox](https://raw.githubusercontent.com/fatinul/mvw/main/images/gruvbox.svg)

- Catppuccin
![Catpuccin](https://raw.githubusercontent.com/fatinul/mvw/main/images/catppuccin.svg)

- Nord
![Nord](https://raw.githubusercontent.com/fatinul/mvw/main/images/nord.svg)
---

## Features

| Features | Notes |
| :----- | :------ |
| **Auto fetch movie data** | Uses [OMDb API](http://www.omdbapi.com/apikey.aspx) behind the hood to fetch movie data fast |
| **Search movies** | Just give the movie title or imdbid to fetch the movie (no more EXACT) |
| **Menu** | List every accessible feature when selected after `mvw list` |
| **Pixelated poster** | Unique way to view the poster __(fully intentional)__ |
| **Configurable poster size** | Can change the poster width |
| **Review history** | All review are saved in a database |
| **Autocomplete** | Provided by the Typer library |
| **Themes** | Gruvbox, Catppuccin, Nord |
| **Save Review** | The review can be saved in svg format with the theme |
| **Worldwide Boxoffice** | Use webscrap tech to find the global box office |
| **Half-star Rating** | Support 0.5 star rating |
| **Review Editor** | Use default editor to edit review |
| **Caching Poster** | No need to download the poster everytime fetching |
| **Easy update** | When searching same movie, will use past review |
| **Reset Config** | Default to the factory setting with single command |
| **Moai help** | Fun gimmick to help you in the process __(can be hide dont worry)__ |

```
  ▁▁     ╭─────────────────────────╮
 ▁▁▁│    │ Why am I at the bottom? │
┌┘└ ░▌   ╰─────────────────────────╯
╚═══╝    F: Cause heroes appear last.. right..                                  
```

---

## Motivation

I have a deep interest in TUI/CLI and also movie in general. I also have a vault in Obsidian where I catalogue   movies that I watch but you know how it goes.. (Legend says that it was still there waiting for me :D)
At first, as someone like me whose personality (TUI + Movie) will obviously create a movie player that does everything (find, _torrent_, play, and done) which has already been done so many times. 
So instead I just want to make something different and that's where I (finally) remember about my Obsidian movie catalogue. Then the code begins..

And _also_, I just want to learn new things :)

Can check my personal blog for more info -> [here](https://fa.tinul.net/blog/build-mvw)
 
---

## Installation

| Method | Command |
| :----- | :------ |
| pipx *(recommended)* | `pipx install mvw` |
| uv | `uv tool install mvw` |
| pip | `pip install mvw` |


> NOTE: This CLI require a nerdfont to have the icon fully showed
> --> This [repo](https://github.com/officialrajdeepsingh/nerd-fonts-installer) seems legit way to install [nerdfont](https://www.nerdfonts.com/) but its up to you how to install, google it, you got this!
> --> Also, If you are on Windows, don't forget to set nerdfont as default font in the settings.

## Usage

```bash
mvw
```

### CLI

```bash
# Configure
mvw config -h

# All configure settings
mvw config --api-key "OMDB API key"       # Required
mvw config --name "Name"                  # Optional
mvw config --poster-width 30
mvw config --theme "gruvbox"
mvw config --moai                         # Toggle
mvw config --review                       # Toggle
mvw config --worldwide-boxoffice          # Toggle
mvw config --reset                        # Toggle

# List all reviewed movies
mvw list

# Preview the reviewed movies
mvw preview --id "ttxxxxxx"
mvd preview --title "Inception"

# Delete the reviewed movies
mvw delete --id "ttxxxxxx"
mvd delete --title "Inception"
```

---

## Configuration

Settings are atuomatically configured using `mvw config`

## FAQ
```
  ▁▁     ╭─────────────────╮
 ▁▁▁│    │ Why am I here?  │
┌┘└ ░▌   ╰─────────────────╯
╚═══╝     F: Just for fun i guess
```

### Why does the poster pixelated?

During the early build of the project, I could not figure out a way to pipe a kitty image into the [iterfzf](https://github.com/dahlia/iterfzf) preview section. It took a long time to process so I try another method which is using [rich_pixel](https://github.com/darrenburns/rich-pixels) library which supports rich and also works on every OS. As of now, thats what I could think of to solve it. TLDR: you can think it as _the intended style_

### Why do I need to register an API key?

**Short answer:** It's easier for me to implement and it's very fast!

**Long answer:** During the early build, I tried to use an API from TMDb, however I found that the registering process are quite intimidating. Then, I found OMDb (which is almost the same as TMDb but easier API key registration). Later down the road, I also tried a no-API-key path [Cinemagoer](https://github.com/cinemagoer/cinemagoer). However, I couldn't (as of now) make it work yet. Naybe in the future, another non-API option will arise?!

### Who is MOAI?

It is just a console.print that I decided to add a face. I choose Moai because, the emoji 🗿 is just too perfect and one of my friends has used it during the phonk era (a lot). The emoji name is also MOAI so I thought why not just MO(AI) it. Same to LLM in [Ollama](https://ollama.com/), just too good to not use.

---

## Inspiration

mvw is built with [Typer](https://github.com/Textualize/textual) + [iterfzf](https://github.com/dahlia/iterfzf) and inspired by:
- [fastfetch](https://github.com/fastfetch-cli/fastfetch) - Visual system information Display.

---

## License

GPL-3.0
