import asyncio

from request_id_helper import request_id_ctx, set_request_id


@set_request_id()
async def build_outbound_headers() -> dict[str, str]:
    await asyncio.sleep(0)
    return {"x-request-id": request_id_ctx.get()}


async def main() -> None:
    headers = await build_outbound_headers()
    assert headers["x-request-id"]
    assert request_id_ctx.get() == ""
    print(headers)


if __name__ == "__main__":
    asyncio.run(main())
