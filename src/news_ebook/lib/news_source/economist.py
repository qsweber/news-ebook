import os
import json
import functools
import requests
from bs4 import BeautifulSoup

import typing
from news_ebook.lib.soup import get_soup_for_url, find_tag, find_tags
from news_ebook.lib.news_source import Paragraph, Article, Section, Issue, NewsSource


class TocArticle(typing.NamedTuple):
    title: str
    link: str


class TocSection(typing.NamedTuple):
    title: str
    articles: typing.List[TocArticle]


@functools.lru_cache()
def _scrape(link: str) -> BeautifulSoup:
    return get_soup_for_url(
        "http://www.economist.com{}".format(link),
        (os.environ["ECONOMIST_USERNAME"], os.environ["ECONOMIST_PASSWORD"]),
    )


def scrape_toc(date: str) -> typing.List[TocSection]:
    issue_url = "/printedition/{}".format(date)

    issue_soup = _scrape(issue_url)

    body = find_tag(issue_soup, "body")

    wtw = TocSection(
        title=find_tag(
            find_tag(body, "div", {"class": "layout-weekly-edition-wtw"}), "h2"
        ).text,
        articles=[
            TocArticle(title=item.text, link=item.attrs["href"])
            for item in find_tags(body, "a", {"class": "weekly-edition-wtw__link"})
        ],
    )

    sections = [
        TocSection(
            title=find_tag(section, "h2").text,
            articles=[
                TocArticle(
                    title=article.text,
                    link=article.attrs["href"],
                )
                for article in find_tags(section, "a")
                if article.text
            ],
        )
        for section in find_tags(
            body, "section", {"class": "layout-weekly-edition-section"}
        )[1:]
    ]

    return [wtw, *sections]


"""
{
    'type': 'IMAGE',
    'url': 'https://www.example.com/20240127_FBD001.jpg',
    'altText': 'Description', (TODO implement scraping this)
    'mode': 'NORMAL',
    'imageType': 'ILLUSTRATION',
    'caption': {'textHtml': ''},
    'credit': 'Foo',
    'source': None,
    'width': 1280,
    'height': 720,
}
"""


def get_image_paragraph(element: typing.Any) -> Paragraph:
    img_data = requests.get(element["url"]).content
    local_image_path = "output/images/{}".format(os.path.basename(element["url"]))

    with open(local_image_path, "wb") as handler:
        handler.write(img_data)

    return Paragraph(
        header=None,
        image_path=local_image_path.strip("output/"),
        text=None,  # Can I do alt-text?
    )


"""
{
    'type': 'PARAGRAPH',
    'text': 'Foo bar',
    'textHtml': '<p>Foo bar</p>'
}
"""


def get_text_paragraph(element: typing.Any) -> Paragraph:
    return Paragraph(header=None, image_path=None, text=element["text"])


def get_paragraph(element: typing.Any) -> typing.Optional[Paragraph]:
    if not element or not element["type"]:
        print("can not find: {}", json.dumps(element))
        return None

    if element["type"] == "IMAGE":
        return get_image_paragraph(element)
    elif element["type"] == "PARAGRAPH":
        return get_text_paragraph(element)

    print("can not parse: {}", json.dumps(element))
    return None


def _parse_and_scrape(article: TocArticle) -> typing.Optional[Article]:
    print("Scraping {}".format(article.link))
    article_soup = _scrape(article.link)

    parsed = json.loads(find_tag(article_soup, "script", {"id": "__NEXT_DATA__"}).text)
    content = parsed["props"]["pageProps"]["cp2Content"]

    if not content:
        print("no cp2Content found")
        return None

    lead = content["leadComponent"]
    body = content["body"]

    elements = [lead, *body]

    return Article(
        title=content["headline"],
        description=content["rubric"],
        paragraphs=[p for p in [get_paragraph(element) for element in elements] if p],
    )


class Economist(NewsSource):
    def get_latest(self) -> Issue:
        date = "2024-01-27"

        sections = scrape_toc(date)
        issue = Issue(
            title="Economist {}".format(date),
            sections=[
                Section(
                    title=section.title,
                    articles=[
                        a
                        for a in [
                            _parse_and_scrape(article)
                            for article in section.articles
                            if not article.link.startswith("/interactive")
                        ]
                        if a
                    ],
                )
                for section in sections
                if section.title != "Economic & financial indicators"
                and section.title != "Graphic detail"
                and section.title != "The world this week"
            ],
        )

        return issue
