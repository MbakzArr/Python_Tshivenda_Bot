import os
import sys

# Minimal colour helper. Falls back to plain text when the terminal
# cannot handle escape codes, so output stays readable everywhere.

ENABLED = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

if os.name == "nt" and ENABLED:
    os.system("")

CODES = {
    "reset": "\033[0m", "bold": "\033[1m", "dim": "\033[2m",
    "red": "\033[31m", "green": "\033[32m", "yellow": "\033[33m",
    "blue": "\033[34m", "cyan": "\033[36m",
}


def c(text, *styles):
    if not ENABLED:
        return text
    pre = "".join(CODES.get(s, "") for s in styles)
    return pre + text + CODES["reset"] if pre else text


def bot(text):
    print(c("Bot:", "cyan", "bold"), text)


def warn(text):
    print(c("  " + text, "yellow"))


def rule(width=52):
    print(c("-" * width, "dim"))


def banner(stats):
    print()
    print(c("  Tshivenda Bot 2.0", "bold", "green"))
    print(c("  %d dictionary entries, %d categories"
            % (stats["entries"], stats["categories"]), "dim"))
    rule()
    bot("Ndaa! Aa! Type a word or a sentence and I will translate it.")
    print(c("     Type /help for commands, or 'ndi zwone' to leave.", "dim"))
    print()
