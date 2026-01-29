import logging


# Example 1: WITHOUT __init__ (This will fail!)
class BrokenFormatter(logging.Formatter):
    ANSI_COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "RESET": "\033[0m",
    }

    def format(self, record):
        if record.levelname in self.ANSI_COLORS:
            record.levelname = f"{self.ANSI_COLORS[record.levelname]}{record.levelname}{self.ANSI_COLORS['RESET']}"
        return super().format(record)


# Example 2: WITH __init__ (This works correctly)
class WorkingFormatter(logging.Formatter):
    ANSI_COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "RESET": "\033[0m",
    }

    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)

    def format(self, record):
        if record.levelname in self.ANSI_COLORS:
            record.levelname = f"{self.ANSI_COLORS[record.levelname]}{record.levelname}{self.ANSI_COLORS['RESET']}"
        return super().format(record)


# Let's test both:
if __name__ == "__main__":
    try:
        # This will raise TypeError because BrokenFormatter doesn't handle the format string
        broken = BrokenFormatter("%(asctime)s - %(levelname)s - %(message)s")
        print("BrokenFormatter worked (unexpected!)")
    except TypeError as e:
        print(f"BrokenFormatter failed as expected: {e}")

    try:
        # This will work correctly because WorkingFormatter properly handles the format string
        working = WorkingFormatter("%(asctime)s - %(levelname)s - %(message)s")
        print("WorkingFormatter worked as expected")
    except TypeError as e:
        print(f"WorkingFormatter failed (unexpected!): {e}")
