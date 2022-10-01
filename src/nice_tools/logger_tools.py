import typing as t

import logging
from logging.handlers import TimedRotatingFileHandler

from threading import Thread
from uuid import uuid4

from telegram import Bot
from telegram.utils.request import Request

import os


__all__ = [
    'ColoredFormatter',
    'TelegramHandler',
    'NiceLogger',
    'BotLogger'
]


_FORMAT = "%(asctime)s - (%(lineno)d):[%(levelname)s] --> %(message)s"


def _make_message(msg: str, f_name: t.Optional[str], *args, **kwargs):
    _msg = f'[{f_name}] - {msg}'

    if args and len(args) > 0:
        _msg += f' | {args}'
    if kwargs and len(kwargs) > 0:
        _msg += f' | {kwargs}'

    return _msg


# ----- # Logger config # ----
class ColoredFormatter(logging.Formatter):
    def __init__(
            self,
            name: str,
            fmt: str = _FORMAT,
            colored: bool = True
    ):
        grey = '\033[90m'
        blue = '\033[94m'
        yellow = '\033[93m'
        red = '\033[91m'
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"

        __format = f'[{name}] - {fmt}'

        if colored:
            self.formats = {
                logging.DEBUG: blue + __format + reset,
                logging.INFO: grey + __format + reset,
                logging.WARNING: yellow + __format + reset,
                logging.ERROR: red + __format + reset,
                logging.CRITICAL: bold_red + __format + reset
            }
        else:
            self.formats = {
                logging.DEBUG: __format,
                logging.INFO: __format,
                logging.WARNING: __format,
                logging.ERROR: __format,
                logging.CRITICAL: __format
            }
        super().__init__(__format)

    def format(self, record):
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class TelegramHandler(logging.Handler):
    def __init__(
            self,
            bot_token: str,
            chat_ids: t.List[int],
            run_async: bool = True,
            fmt: str = "[%(levelname)s]\n%(lineno)d - %(funcName)s:\n\n%(message)s"
    ):
        super().__init__()
        self.bot = Bot(bot_token)
        self.chat_ids = chat_ids
        self.fmt = fmt

        self._MAX_LEN = 4096

        self.run_async = run_async

    def _send_message(self, msg: str):
        for chat_id in self.chat_ids:
            self.bot.send_message(chat_id, msg)

    def _send_document(self, doc: str):
        for chat_id in self.chat_ids:
            self.bot.send_document(chat_id, doc)

    def _send_as_document(self, msg: str):
        rand_name = str(uuid4()).split('-')[0]
        with open(f'logs/{rand_name}-logs.txt', 'w') as f:
            f.write(msg)
        return self._send_document(f'logs/{rand_name}-logs.txt')

    def send(self, msg: str):
        try:
            if len(msg) > self._MAX_LEN:
                self._send_as_document(msg)
            else:
                self._send_message(msg)
        except Exception as e:
            print(e)

    def emit(self, record: logging.LogRecord):
        msg = self.format(record)
        if self.run_async:
            Thread(target=self.send, args=(msg,)).start()
        else:
            self.send(msg)

    def format(self, record: logging.LogRecord):
        log_fmt = self.fmt
        formatter = logging.Formatter(log_fmt)

        return formatter.format(record)


class NiceLogger(logging.Logger):
    @staticmethod
    def _make_folder(folder: str = 'logs') -> None:
        if not os.path.exists(folder):
            os.mkdir(folder)

    def __init__(
            self,
            name: str,
            fmt: str = _FORMAT,
            enable_file: bool = True,
            enable_telegram: bool = False,
            telegram_token: str = None,
            telegram_chat_ids: t.List[int] = None,
            tele_run_async: bool = True,
            colored: bool = True,
            when="midnight",
            backup_count: int = 2,
            encoding: str = "utf-8",
            log_folder: str = 'logs'
    ):
        self.__enable_file = enable_file
        self.__enable_telegram = enable_telegram
        self.__telegram_token = telegram_token
        self.__telegram_chat_ids = telegram_chat_ids
        self.__tele_run_async = tele_run_async

        self.__handle_telegram()

        super().__init__(name)
        self.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(ColoredFormatter(name, fmt, colored))
        self.addHandler(ch)

        if self.__enable_file is True:
            self._make_folder(log_folder)

            th = TimedRotatingFileHandler(
                filename=f"logs/{name}-logs",
                when=when,
                backupCount=backup_count,
                encoding=encoding
            )
            th.setLevel(logging.DEBUG)
            th.setFormatter(ColoredFormatter(name, fmt, colored=False))
            self.addHandler(th)

        if self.__enable_telegram:
            tgh = TelegramHandler(self.__telegram_token, self.__telegram_chat_ids, self.__tele_run_async)
            self.addHandler(tgh)

    def __handle_telegram(self):
        if self.__enable_telegram and self.__telegram_token is None:
            raise ValueError("When enable_telegram is True, Telegram token is required")

        if self.__enable_telegram and self.__telegram_chat_ids is None:
            raise ValueError("When enable_telegram is True, Telegram chat ids are required")

        if self.__telegram_chat_ids is not None and self.__telegram_token is not None:
            self.__enable_telegram = True

    def info(self, msg: t.Any, f_name: t.Optional[str] = 'info', *args: t.Any, **kwargs: t.Any) -> None:
        msg = _make_message(msg, f_name, *args, **kwargs)
        super().info(msg)

    def debug(self, msg: t.Any, f_name: t.Optional[str] = 'debug', *args: t.Any, **kwargs: t.Any) -> None:
        msg = _make_message(msg, f_name, *args, **kwargs)
        super().debug(msg)

    def warning(self, msg: t.Any, f_name: t.Optional[str] = 'warning', *args: t.Any, **kwargs: t.Any) -> None:
        msg = _make_message(msg, f_name, *args, **kwargs)
        super().warning(msg)

    def error(self, msg: t.Any, f_name: t.Optional[str] = 'error', *args: t.Any, **kwargs: t.Any) -> None:
        msg = _make_message(msg, f_name, *args, **kwargs)
        super().error(msg)

    def critical(self, msg: t.Any, f_name: t.Optional[str] = 'critical', *args: t.Any, **kwargs: t.Any) -> None:
        msg = _make_message(msg, f_name, *args, **kwargs)
        super().critical(msg)

    def exception(self, msg: t.Any, f_name: t.Optional[str] = 'exception', *args: t.Any, **kwargs: t.Any) -> None:
        msg = _make_message(msg, f_name, *args, **kwargs)
        super().exception(msg)


class BotLogger:
    def __init__(self, name: str, token: str, chat_ids: t.List[int], run_async: bool = True, proxy: str = None):
        self.__name = name
        self.__token = token
        self.__chat_ids = chat_ids
        self.__run_async = run_async

        self._MAX_LEN = 4096

        if proxy is not None:
            self.__bot = Bot(token=self.__token, request=Request(proxy_url=proxy))
        else:
            self.__bot = Bot(token=self.__token)

        return

    def __call__(self, *args, **kwargs):
        return self.log(*args, **kwargs)

    def _send_message(self, msg: str):
        for chat_id in self.__chat_ids:
            self.__bot.send_message(chat_id, msg)

    def _send_document(self, doc: str):
        for chat_id in self.__chat_ids:
            self.__bot.send_document(chat_id, doc)

    def _send_as_document(self, msg: str):
        rand_name = str(uuid4()).split('-')[0]
        with open(f'logs/{rand_name}-logs.txt', 'w') as f:
            f.write(msg)
        return self._send_document(f'logs/{rand_name}-logs.txt')

    def log(self, msg: str, f_name: str = 'log', *args: t.Any, **kwargs: t.Any) -> None:
        _msg = _make_message(msg, f_name, *args, **kwargs)
        __msg = f'[{self.__name}]\n\n' \
                f'{_msg}'
        try:
            if len(__msg) > self._MAX_LEN:
                if self.__run_async:
                    Thread(target=self._send_as_document, args=(__msg,)).start()
                else:
                    self._send_as_document(__msg)
            else:
                if self.__run_async:
                    Thread(target=self._send_message, args=(__msg,)).start()
                else:
                    self._send_message(__msg)
        except Exception as e:
            print(e)
