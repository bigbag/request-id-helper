import logging

from request_id_helper import RequestIdFormatter, request_id_ctx, set_request_id

handler = logging.StreamHandler()
handler.setFormatter(RequestIdFormatter("%(levelname)s [%(request_id)s] %(message)s"))
logger = logging.getLogger("request-id-example")
logger.handlers = [handler]
logger.setLevel(logging.INFO)
logger.propagate = False


@set_request_id()
def process_order() -> str:
    request_id = request_id_ctx.get()
    logger.info("processing order")
    return request_id


if __name__ == "__main__":
    print(process_order())
