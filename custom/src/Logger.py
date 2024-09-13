import logging
from logging.handlers import TimedRotatingFileHandler


class FormatterWithHeader(logging.Formatter):
    def __init__(
        self,
        header: str,
        fmt: str = "%(asctime)s\t[%(levelname)s]:\t%(message)s",
        datefmt: str = "%Y-%m-%d %H:%M:%S",
        style: str = "%",
    ) -> None:
        super().__init__(fmt, datefmt, style)
        self.header = header
        self.format = self.first_line_format

    def first_line_format(self, record):
        self.format = super().format
        return self.header + "\n" + self.format(record)


class Logger:
    def __init__(self, name: str, header: str) -> None:
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        handler = TimedRotatingFileHandler(
            f"logs/{name}.log",
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8",
        )
        handler.suffix = "%Y-%m-%d_%H-%M-%S.log"
        handler.setLevel(logging.DEBUG)
        actual_header = f"time\tlevel\t{header}"
        dev_formatter = FormatterWithHeader(actual_header)
        handler.setFormatter(dev_formatter)

        self.logger.addHandler(handler)

    def get_logger(self):
        return self.logger
