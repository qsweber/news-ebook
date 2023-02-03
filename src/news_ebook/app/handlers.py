import logging
import typing

from raven import Client  # type: ignore
from raven.transport.requests import RequestsHTTPTransport  # type: ignore

from news_ebook.clients.sqs import SqsMessage
from news_ebook.app.service_context import service_context


sentry = Client(transport=RequestsHTTPTransport)
logger = logging.getLogger(__name__)


def cronHandler(func: typing.Callable[[], None]) -> typing.Callable[[], None]:
    def wrapper() -> None:
        try:
            func()
        except Exception:
            sentry.captureException()
            raise

    return wrapper


@cronHandler
def time_driven_task() -> None:
    logger.info("it's time!")
