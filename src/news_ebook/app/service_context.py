from typing import NamedTuple

from news_ebook.clients.ses import SesClient


class Clients(NamedTuple):
    ses: SesClient


class ServiceContext(NamedTuple):
    clients: Clients


service_context = ServiceContext(
    clients=Clients(
        ses=SesClient(),
    )
)
