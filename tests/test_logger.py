import logging
from collections.abc import Generator
from logging import LogRecord
from typing import Any

import pytest

from request_id_helper import LogExtraFactory, RequestIdFormatter, init_logger, request_id_ctx


@pytest.fixture
def restore_record_factory() -> Generator[None, None, None]:
    factory = logging.getLogRecordFactory()
    try:
        yield
    finally:
        logging.setLogRecordFactory(factory)


def test_log_extra_factory_uses_context_or_fallback() -> None:
    request_id_ctx.set("request-123")
    record = LogExtraFactory("name", logging.INFO, __file__, 1, "message", (), None)
    request_id_ctx.reset()
    fallback = LogExtraFactory("name", logging.INFO, __file__, 1, "message", (), None)

    assert record.request_id == "request-123"
    assert fallback.request_id == "N/A"


def test_formatter_adds_fallback_without_overwriting_a_record_id() -> None:
    formatter = RequestIdFormatter("%(request_id)s %(message)s")
    missing = logging.LogRecord("name", logging.INFO, __file__, 1, "message", (), None)
    present = logging.LogRecord("name", logging.INFO, __file__, 1, "message", (), None)
    present.request_id = "caller-id"

    assert formatter.format(missing) == "N/A message"
    assert formatter.format(present) == "caller-id message"


def test_init_logger_preserves_fields_from_the_existing_factory(
    restore_record_factory: None,
) -> None:
    default_factory = logging.getLogRecordFactory()

    def existing_factory(*args: Any, **kwargs: Any) -> LogRecord:
        record = default_factory(*args, **kwargs)
        record.trace_id = "trace-123"
        return record

    logging.setLogRecordFactory(existing_factory)
    init_logger({"version": 1, "disable_existing_loggers": False})
    record = logging.getLogRecordFactory()("name", logging.INFO, __file__, 1, "message", (), None)

    assert record.trace_id == "trace-123"
    assert record.request_id == "N/A"


def test_init_logger_does_not_replace_a_request_id_already_on_a_record(
    restore_record_factory: None,
) -> None:
    default_factory = logging.getLogRecordFactory()

    def existing_factory(*args: Any, **kwargs: Any) -> LogRecord:
        record = default_factory(*args, **kwargs)
        record.request_id = "caller-id"
        return record

    logging.setLogRecordFactory(existing_factory)
    init_logger({"version": 1, "disable_existing_loggers": False})
    record = logging.getLogRecordFactory()("name", logging.INFO, __file__, 1, "message", (), None)

    assert record.request_id == "caller-id"


def test_init_logger_is_idempotent(restore_record_factory: None) -> None:
    init_logger({"version": 1, "disable_existing_loggers": False})
    factory = logging.getLogRecordFactory()
    init_logger({"version": 1, "disable_existing_loggers": False})

    assert logging.getLogRecordFactory() is factory


def test_init_logger_enriches_emitted_records(restore_record_factory: None) -> None:
    records: list[LogRecord] = []

    class CapturingHandler(logging.Handler):
        def emit(self, record: LogRecord) -> None:
            records.append(record)

    logger = logging.getLogger("request-id-helper.tests.emitted-record")
    handler = CapturingHandler()
    previous_handlers = logger.handlers[:]
    previous_level = logger.level
    previous_propagate = logger.propagate
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False
    try:
        init_logger({"version": 1, "disable_existing_loggers": False})
        request_id_ctx.set("request-123")
        logger.info("message")
        request_id_ctx.reset()

        assert len(records) == 1
        assert records[0].request_id == "request-123"
        assert records[0].getMessage() == "message"
    finally:
        logger.handlers = previous_handlers
        logger.setLevel(previous_level)
        logger.propagate = previous_propagate


def test_init_logger_wraps_a_factory_installed_later(restore_record_factory: None) -> None:
    default_factory = logging.getLogRecordFactory()
    init_logger({"version": 1, "disable_existing_loggers": False})

    def external_factory(*args: Any, **kwargs: Any) -> LogRecord:
        record = default_factory(*args, **kwargs)
        record.external_trace_id = "trace-123"
        return record

    logging.setLogRecordFactory(external_factory)
    init_logger({"version": 1, "disable_existing_loggers": False})
    record = logging.getLogRecordFactory()("name", logging.INFO, __file__, 1, "message", (), None)

    assert record.external_trace_id == "trace-123"
    assert record.request_id == "N/A"
