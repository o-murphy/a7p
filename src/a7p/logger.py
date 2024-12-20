import sys
import logging

# ANSI escape codes for colors
RESET = "\033[0m"
COLORS = {
    "DEBUG": "\033[34m",  # Blue
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[35m",  # Magenta

    "ORANGE": "\033[38;5;214m",  # Approximation of Orange using 256-color mode
    "CYAN": "\033[36m",  # Cyan
    "LIGHT_GRAY": "\033[37m",  # Light Gray
    "DARK_GRAY": "\033[90m",  # Dark Gray
    "LIGHT_BLUE": "\033[94m",  # Light Blue
    "LIGHT_GREEN": "\033[92m",  # Light Green
    "LIGHT_YELLOW": "\033[93m",  # Light Yellow
    "LIGHT_RED": "\033[91m",  # Light Red
    "RESET": "\033[0m"  # Reset
}


class ANSILoggerFormatter(logging.Formatter):
    def format(self, record):
        log_color = COLORS.get(record.levelname, RESET)
        formatted_message = f"{record.levelname.ljust(len('CRITICAL'))}: {super().format(record)}"
        return f"{log_color}{formatted_message}{RESET}"


# formatter = logging.Formatter("%(levelname)s:%(message)s")
formatter = ANSILoggerFormatter()
stream_handler = logging.StreamHandler(sys.stdout)  # Use sys.stdout here
stream_handler.setFormatter(formatter)

logger = logging.getLogger("a7p")
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)  # Only add this handler
logger.propagate = False


def color_fmt(*args, levelname: str = "", sep=" "):
    return f"{COLORS.get(levelname.upper(), RESET)}{sep.join(args)}{RESET}"


def color_print(*args, levelname: str = "", sep=" ", end="\n"):
    print(color_fmt(*args, levelname=levelname, sep=sep), end=end, flush=True)


__all__ = (
    'logger',
    'COLORS',
    'RESET',
    'color_fmt',
    'color_print',
)
