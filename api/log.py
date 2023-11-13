import logging

import colorama


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': colorama.Fore.BLUE,
        'INFO': colorama.Fore.GREEN,
        'WARNING': colorama.Fore.YELLOW,
        'ERROR': colorama.Fore.RED,
        'CRITICAL': colorama.Fore.MAGENTA,
    }

    def format(self, record):
        log_message = super().format(record)
        log_level_color = self.COLORS.get(record.levelname, colorama.Fore.RESET)
        return log_level_color + log_message + colorama.Fore.RESET


class ColoredLogger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)
        self.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(ColoredFormatter("[%(asctime)s | %(levelname)s] %(message)s"))
        self.addHandler(handler)


__log = ColoredLogger(__name__)

colorama.init()


def info(msg: str):
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(msg + '\n')
    __log.info(msg)


def debug(msg: str):
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(msg + '\n')
    __log.debug(msg)


def error(msg: str):
    with open('log.txt', 'a', encoding='utf-8') as f:
        f.write(msg + '\n')
    __log.error(msg)
