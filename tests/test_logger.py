import logging

from request_id_helper import LogExtraFactory, RequestIdFormatter, init_logger, request_id_ctx


class MockLogHandler(logging.Handler):
    records = []

    def emit(self, record):
        self.records.append(f"[{record.request_id}] {record.message}")


def test_log_extra_factory(caplog):
    REQUEST_ID = "REQUEST_ID"
    mock_logger = MockLogHandler()
    logger = logging.getLogger()
    logging.setLogRecordFactory(LogExtraFactory)
    logger.addHandler(mock_logger)

    request_id_ctx.set(REQUEST_ID)
    logger.error("an error")

    request_id_ctx.set(None)
    logger.error("an error")

    assert REQUEST_ID in mock_logger.records[0]
    assert "N/A" in mock_logger.records[1]

    request_id_ctx.reset()


def test_init_logger():
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": 0,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s [%(request_id)s] %(name)s | %(message)s",
                "datefmt": "%d/%b/%Y %H:%M:%S",
            }
        },
        "handlers": {
            "stdout": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "loggers": {
            "": {
                "handlers": ["stdout"],
                "propagate": True,
                "level": "INFO",
            },
        },
    }
    init_logger(LOGGING)
    logger = logging.getLogger()
    assert len(logger.handlers) == 1


def test_request_id_not_present():
    formatter = RequestIdFormatter("%(request_id)s - %(message)s")
    record = logging.LogRecord("test_logger", logging.INFO, "", 0, "Test message", None, None)
    formatted_message = formatter.format(record)
    assert formatted_message == "N/A - Test message"


def test_request_id_present():
    formatter = RequestIdFormatter("%(request_id)s - %(message)s")
    record = logging.LogRecord("test_logger", logging.INFO, "", 0, "Test message", None, None)
    record.request_id = "12345"
    formatted_message = formatter.format(record)
    assert formatted_message == "12345 - Test message"


def test_request_id_empty_string():
    formatter = RequestIdFormatter("%(request_id)s - %(message)s")
    record = logging.LogRecord("test_logger", logging.INFO, "", 0, "Test message", None, None)
    record.request_id = ""
    formatted_message = formatter.format(record)
    assert formatted_message == " - Test message"


def test_custom_format_string():
    formatter = RequestIdFormatter("[%(request_id)s] %(levelname)s: %(message)s")
    record = logging.LogRecord(
        "test_logger", logging.WARNING, "", 0, "Custom format test", None, None
    )
    formatted_message = formatter.format(record)
    assert formatted_message == "[N/A] WARNING: Custom format test"


def test_request_id_not_overwritten():
    formatter = RequestIdFormatter("%(request_id)s - %(message)s")
    record = logging.LogRecord("test_logger", logging.INFO, "", 0, "Test message", None, None)
    record.request_id = "existing_id"
    formatted_message = formatter.format(record)
    assert formatted_message == "existing_id - Test message"
    assert record.request_id == "existing_id"
