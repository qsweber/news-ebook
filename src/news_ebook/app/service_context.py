from typing import NamedTuple

from news_ebook.clients.sqs import SqsClient


class Clients(NamedTuple):
    sqs: SqsClient


class ServiceContext(NamedTuple):
    clients: Clients


service_context = ServiceContext(
    clients=Clients(
        sqs=SqsClient(),
    )
)
