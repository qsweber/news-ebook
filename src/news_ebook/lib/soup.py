import typing

from bs4 import Tag


def find_tag(
    starting_tag: Tag,
    tag_type: str,
    attrs: typing.Optional[typing.Dict[str, str]] = None,
) -> Tag:
    if attrs is None:
        attrs = {}
    tag = starting_tag.find(tag_type, attrs)
    if not tag or not isinstance(tag, Tag):
        raise ValueError("no tag found")
    return tag


def find_tags(
    starting_tag: Tag,
    tag_type: str,
    attrs: typing.Optional[typing.Dict[str, str]] = None,
) -> typing.List[Tag]:
    return starting_tag.findAll(tag_type, attrs)
