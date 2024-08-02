import functools
import io
import os
from requests import session, Session, Response
from PIL import Image, ImageFile

BASE_URL = "https://www.economist.com"


@functools.lru_cache()
def cached_get(s: Session, link: str, attempt: int = 1) -> Response:
    print(f"Getting {link} - attempt {attempt}")
    return s.get(link)


class EconomistClient:
    def __init__(self) -> None:
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

    def get_url(self, url: str) -> Response:
        return cached_get(self.session, f"{BASE_URL}{url}")

    def get_img(self, url: str) -> ImageFile.ImageFile:
        attempt = 1
        while attempt < 3:
            response = cached_get(self.session, url, attempt).content
            try:
                return Image.open(io.BytesIO(response))
            except Exception:
                attempt += 1

        raise Exception("could not parse image")
