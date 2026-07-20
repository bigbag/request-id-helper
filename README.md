# request-id-helper

Context-local request IDs for Python logging and async applications.

## Requirements

- Python 3.11–3.14

## Installation

```console
uv add request-id-helper
```

```console
pip install request-id-helper
```

## Logging and scoped request IDs

Configure a formatter that includes `%(request_id)s`, then decorate each request entry point. The generated ID is available for the complete call and is restored when the call finishes, raises, or is cancelled.

```python
import logging

from request_id_helper import RequestIdFormatter, request_id_ctx, set_request_id

handler = logging.StreamHandler()
handler.setFormatter(RequestIdFormatter("%(levelname)s [%(request_id)s] %(message)s"))
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@set_request_id()
def handle_request() -> None:
    logger.info("handling request")
    assert request_id_ctx.get()
```

`set_request_id()` supports `async def` functions as well. Each decorated call receives an independent ID, including concurrent asyncio tasks. Nested decorated calls temporarily replace the outer ID and restore it when they return.

## Existing logging dictionaries

Use `init_logger()` with an existing `logging.config.dictConfig` dictionary to install request-ID record enrichment. It composes with an already configured log-record factory and never overwrites a record that already has `request_id`.

```python
from request_id_helper import init_logger

init_logger(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": "%(levelname)s [%(request_id)s] %(message)s"}
        },
    }
)
```

`RequestIdFormatter` is an alternative for individual handlers. It uses `N/A` when a record has no request ID.

## Direct context propagation

Read the current value when making an outbound call:

```python
from request_id_helper import request_id_ctx

headers = {"x-request-id": request_id_ctx.get()}
```

Workers can restore a propagated value with `request_id_ctx.set(serialized_request_id)`. Call `request_id_ctx.reset()` when the direct binding is no longer needed.

## Examples

```console
uv run python examples/basic_usage.py
uv run python examples/async_propagation.py
```

## Development

```console
uv sync --all-groups
make lint
make test
make build
```

## License

request-id-helper is distributed under the Apache License 2.0.

## Reporting a security vulnerability

See the [security policy](https://github.com/bigbag/request-id-helper/security/policy).
