import logging
import os
import typing
import datetime

from raven import Client  # type: ignore
from raven.transport.requests import RequestsHTTPTransport  # type: ignore

from news_ebook.app.service_context import service_context
from news_ebook.lib.news_source.economist import Economist
from news_ebook.lib.output.ebook import Output
from news_ebook.lib.output.html import Output as HtmlOutput


sentry = Client(transport=RequestsHTTPTransport)
logger = logging.getLogger(__name__)


def cron_handler(func: typing.Callable[[], None]) -> typing.Callable[[], None]:
    def wrapper() -> None:
        try:
            func()
        except Exception:
            sentry.captureException()
            raise

    return wrapper


@cron_handler
def economist_kindle() -> None:
    logged_in_check = service_context.clients.economist.get_url("/saved-stories")
    if logged_in_check.status_code != 200:
        raise SystemError("not logged in")
    saturday = (
        datetime.datetime.now()
        + datetime.timedelta((5 - datetime.datetime.now().weekday()) % 7)
    ).strftime("%Y-%m-%d")
    output_dir = f"output/{saturday}"
    os.makedirs(output_dir, exist_ok=True)
    economist = Economist(service_context.clients.economist, output_dir, saturday)
    issue = economist.get_latest()
    output = Output()
    html_output = HtmlOutput()
    html_output.get_output_path(issue, output_dir)
    ebook_output = output.get_output_path(issue, output_dir)
    service_context.clients.ses.send_email(
        os.environ["KINDLE_EMAIL"],
        os.environ["FROM_EMAIL"],
        issue.title,
        "See attachment.",
        ebook_output,
    )
