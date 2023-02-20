import typing


class NewsArticle(typing.NamedTuple):
    headline: str
    description: str
    local_image_path: str
    article_body: str


class Section(typing.NamedTuple):
    headline: str
    articles: typing.List[NewsArticle]


class Ebook(typing.NamedTuple):
    title: str
    sections: typing.List[Section]
