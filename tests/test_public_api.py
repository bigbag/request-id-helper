import request_id_helper


def test_public_api_has_the_expected_exports() -> None:
    assert request_id_helper.__all__ == [
        "LogExtraFactory",
        "RequestIdFormatter",
        "RequestIdCtx",
        "init_logger",
        "request_id_ctx",
        "set_request_id",
        "__version__",
    ]


def test_public_api_exports_are_importable() -> None:
    from request_id_helper import (
        LogExtraFactory,
        RequestIdCtx,
        RequestIdFormatter,
        init_logger,
        request_id_ctx,
        set_request_id,
    )

    assert all(
        value is not None
        for value in (
            LogExtraFactory,
            RequestIdCtx,
            RequestIdFormatter,
            init_logger,
            request_id_ctx,
            set_request_id,
        )
    )
