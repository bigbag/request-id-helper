from collections.abc import Callable
from logging import Formatter, LogRecord, getLogRecordFactory, setLogRecordFactory
from logging.config import dictConfig
from typing import Any

from .helper import request_id_ctx

RecordFactory = Callable[..., LogRecord]
_base_record_factory: RecordFactory | None = None


def _add_request_id(record: LogRecord) -> LogRecord:
    record.__dict__.setdefault("request_id", request_id_ctx.get() or "N/A")
    return record


def _request_id_record_factory(*args: Any, **kwargs: Any) -> LogRecord:
    if _base_record_factory is None:
        raise RuntimeError("Request ID record factory has not been initialized")
    return _add_request_id(_base_record_factory(*args, **kwargs))


class LogExtraFactory(LogRecord):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        _add_request_id(self)


def init_logger(config: dict[str, Any]) -> None:
    global _base_record_factory

    dictConfig(config)
    current_factory = getLogRecordFactory()
    if current_factory is _request_id_record_factory:
        return
    _base_record_factory = current_factory
    setLogRecordFactory(_request_id_record_factory)


class RequestIdFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        record.__dict__.setdefault("request_id", "N/A")
        return super().format(record)
