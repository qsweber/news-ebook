from bs4 import Tag
import typing


def find_tag(starting_tag: Tag, type: str, attrs: typing.Dict[str, str] = {}) -> Tag:
    tag = starting_tag.find(type, attrs)
    if not tag or not isinstance(tag, Tag):
        raise Exception("no tag found")
    return tag


def find_tags(
    starting_tag: Tag, type: str, attrs: typing.Dict[str, str] = {}
) -> typing.List[Tag]:
    return starting_tag.findAll(type, attrs)
