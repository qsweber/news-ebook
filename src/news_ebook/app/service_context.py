from typing import NamedTuple

from news_ebook.clients.ses import SesClient
from news_ebook.clients.economist import EconomistClient


class Clients(NamedTuple):
    ses: SesClient
    economist: EconomistClient


class ServiceContext(NamedTuple):
    clients: Clients


service_context = ServiceContext(
    clients=Clients(
        ses=SesClient(),
        economist=EconomistClient(),
    )
)
