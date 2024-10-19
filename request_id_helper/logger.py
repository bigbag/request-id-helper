from logging import Formatter, LogRecord, setLogRecordFactory
from logging.config import dictConfig
from typing import Any, Dict

from . import helper


class LogExtraFactory(LogRecord):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request_id = helper.request_id_ctx.get() or "N/A"

        self.__dict__["request_id"] = request_id


def init_logger(config: Dict[str, Any]):
    dictConfig(config)
    setLogRecordFactory(LogExtraFactory)


class RequestIdFormatter(Formatter):
    def format(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = "N/A"
        return super().format(record)
