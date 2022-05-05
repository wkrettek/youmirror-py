"""
This module is for pretty printing on the output
"""
_colors = {
    "header": "\033[95m",
    "blue": "\033[94m",
    "cyan": "\033[96m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "endc": "\033[0m",
    "bold": "\033[1m",
    "underline": "\033[4m",
}


def human_readable(num, suffix="B"):
    """
    Takes an integer number of bytes and converts to a human readable form
    """
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def color(s: str, color: str):
    """
    Takes the text and wraps it in the chosen format
    """
    return _colors[color] + s + _colors["endc"]
