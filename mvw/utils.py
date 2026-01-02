from rich.text import Text

def is_nerd_font_installed():
    """
    Checks if Nerd Font icons render with expected width.
    Note: This isn't 100% foolproof but works for most modern terminals.
    """
    # Use a common Nerd Font icon (e.g., the folder icon \uf07b)
    icon = "\uf07b" 

    # We measure how many 'columns' the terminal thinks this character takes
    # If the font isn't a Nerd Font, the terminal often treats it as a 
    # narrow unknown character or a double-width placeholder.
    # In a Nerd Font environment, these are usually defined correctly.
    width = Text(icon).cell_len

    # This is a heuristic: most Nerd Fonts render these as 1 or 2 cells.
    # If it returns 0 or the terminal environment variable isn't set up 
    # to handle UTF-8, we can assume a warning is needed.
    return width > 0

if __name__ == "__main__":
    print(is_nerd_font_installed())
