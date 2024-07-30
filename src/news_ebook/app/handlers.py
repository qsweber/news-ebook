import logging
import os
import typing

from raven import Client  # type: ignore
from raven.transport.requests import RequestsHTTPTransport  # type: ignore

from news_ebook.app.service_context import service_context
from news_ebook.lib.news_source.economist import Economist
from news_ebook.lib.output.ebook import Output


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
def economist_kindle() -> None:
    logged_in_check = service_context.clients.economist.get_url("/saved-stories")
    if logged_in_check.status_code != 200:
        raise Exception("not logged in")
    economist = Economist(service_context.clients.economist)
    issue = economist.get_latest()
    output = Output()
    ebook_output = output.get_output_path(issue)
    service_context.clients.ses.send_email(
        os.environ["KINDLE_EMAIL"],
        os.environ["FROM_EMAIL"],
        issue.title,
        "See attachment.",
        ebook_output,
    )
