import requests

from bs4 import BeautifulSoup, Tag
import typing


def get_soup_for_url(url: str, auth: typing.Tuple[str, str]) -> BeautifulSoup:
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, auth=auth)

    return BeautifulSoup(response.text, "html.parser")


def find_tag(starting_tag: Tag, type: str, attrs: typing.Dict[str, str] = {}) -> Tag:
    tag = starting_tag.find(type, attrs)
    if not tag or not isinstance(tag, Tag):
        raise Exception("not a tag")
    return tag


def find_tags(
    starting_tag: Tag, type: str, attrs: typing.Dict[str, str] = {}
) -> typing.List[Tag]:
    return starting_tag.findAll(type, attrs)
