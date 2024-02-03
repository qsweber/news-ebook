import os
import logging
import json

from flask import Flask, jsonify, request, Response
from raven import Client  # type: ignore
from raven.contrib.flask import Sentry  # type: ignore
from raven.transport.requests import RequestsHTTPTransport  # type: ignore

from news_ebook.app.service_context import service_context
from news_ebook.clients.ses import Attachment
from news_ebook.lib.news_source.economist import Economist
from news_ebook.lib.output.ebook import Output as EbookOutput

app = Flask(__name__)
sentry = Sentry(
    app,
    client=Client(
        transport=RequestsHTTPTransport,
    ),
)
logger = logging.getLogger(__name__)


@app.route("/api/v0/status", methods=["GET"])
def status() -> Response:
    logger.info("received request {}".format(json.dumps(request.json)))

    response = jsonify({"text": "ok"})
    response.headers.add("Access-Control-Allow-Origin", "*")

    return response


def economist_ebook() -> Response:
    economist = Economist()
    issue = economist.get_latest()
    ebook_output = EbookOutput()
    output_path = ebook_output.get_output_path(issue)

    with open(output_path) as f:
        content = f.read()
        service_context.clients.ses.send_email(
            os.environ["TO_EMAIL"],
            os.environ["FROM_EMAIL"],
            issue.title,
            "see attachment",
            Attachment(output_path, content),
        )

    response = jsonify({"text": "ok"})
    response.headers.add("Access-Control-Allow-Origin", "*")

    return response
