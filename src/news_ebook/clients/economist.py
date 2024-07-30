import functools
import os
from requests import session, Session, Response

BASE_URL = "https://www.economist.com"


@functools.lru_cache()
def cached_get(session: Session, link: str) -> Response:
    return session.get(link)


class EconomistClient:
    def __init__(self):
        self.session = session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})
        self.session.cookies.update(
            {
                "fcx_access_token": os.environ["ECONOMIST_FCX_ACCESS_TOKEN"],
                "fcx_refresh_token": os.environ["ECONOMIST_FCX_REFRESH_TOKEN"],
                "fcx_access_state": os.environ["ECONOMIST_FCX_ACCESS_STATE"],
                "fcx_user": os.environ["ECONOMIST_FCX_USER"],
            },
        )

    def get_url(self, url):
        return cached_get(self.session, "{}{}".format(BASE_URL, url))
