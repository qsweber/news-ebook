import functools
import io
import os
from requests import session, Session, Response
from PIL import Image

BASE_URL = "https://www.economist.com"


@functools.lru_cache()
def cached_get(s: Session, link: str) -> Response:
    print(f"Getting {link}")
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

    def get_img(self, url: str, output_file: str) -> None:
        img_data = cached_get(self.session, url).content
        if "Enable JavaScript" in str(img_data):
            print("Got blocked by Cloudflare")
            raise SystemError("Blocked by Cloudflare")

        with open(output_file, "wb") as handler:
            handler.write(img_data)

        img = Image.open(io.BytesIO(img_data))
        desired_width = 600
        resized_height = int(
            (float(img.size[1]) * float(desired_width / float(img.size[0])))
        )
        img.thumbnail((desired_width, resized_height))
        img.save(output_file)
