from typing import NamedTuple, Optional, List


class Paragraph(NamedTuple):
    header: Optional[str]
    text: Optional[str]
    image_path: Optional[str]


class Article(NamedTuple):
    title: str
    description: str
    paragraphs: List[Paragraph]


class Section(NamedTuple):
    title: str
    articles: List[Article]


class Issue(NamedTuple):
    title: str
    sections: List[Section]


class NewsSource:
    def get_latest(self) -> Issue:
        raise NotImplementedError("get_latest not implemented")
