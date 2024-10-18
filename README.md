# request-id-helper

[![CI](https://github.com/bigbag/request-id-helper/workflows/CI/badge.svg)](https://github.com/bigbag/request-id-helper/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/bigbag/request-id-helper/branch/main/graph/badge.svg?token=ZRUN7SUKB2)](https://codecov.io/gh/bigbag/request-id-helper)
[![pypi](https://img.shields.io/pypi/v/request-id-helper.svg)](https://pypi.python.org/pypi/request-id-helper)
[![downloads](https://img.shields.io/pypi/dm/request-id-helper.svg)](https://pypistats.org/packages/request-id-helper)
[![versions](https://img.shields.io/pypi/pyversions/request-id-helper.svg)](https://github.com/bigbag/request-id-helper)
[![license](https://img.shields.io/github/license/bigbag/request-id-helper.svg)](https://github.com/bigbag/request-id-helper/blob/master/LICENSE)


**request-id-helper** is a helper to add request id in logger and context.

* [Project Changelog](https://github.com/bigbag/request-id-helper/blob/main/CHANGELOG.md)

## Installation

request-id-helper is available on PyPI.
Use pip to install:

    $ pip install request-id-helper

## Basic Usage

```py
import logging
from request_id_helper import init_logger, set_request_id

logger = logging.getLogger(__name__)

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


def main():
    init_logger(LOGGING)

    @set_request_id()
    def my_function() -> int:
        
        logger.info("Demo")

        return 10

    my_function()

if __name__ == "__main__":
    main()

```


```bash
    [17/Oct/2024 20:13:02] INFO [459cb386-5947-4eec-b3d8-266605f40444] __main__ | Demo
```
## License

request-id-helper is developed and distributed under the Apache 2.0 license.

## Reporting a Security Vulnerability

See our [security policy](https://github.com/bigbag/request-id-helper/security/policy).
