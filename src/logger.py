from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"


def create_log_file():
    """
    Creates a new log file for one agent run.
    """

    LOG_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = LOG_DIR / f"agent_run_{timestamp}.txt"

    log_file.write_text("Agent run log\n", encoding="utf-8")

    return log_file


def write_log(log_file, text):
    """
    Appends the text to the current log file.
    """

    with log_file.open("a", encoding="utf-8") as file:
        file.write(text + "\n")
