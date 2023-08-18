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


def _parse_and_scrape(article: TocArticle) -> Article:
    print("Scraping {}".format(article.link))
    article_soup = _scrape(article.link)

    parsed = json.loads(
        find_tag(
            find_tag(article_soup, "head"), "script", {"type": "application/ld+json"}
        ).text
    )

    print(parsed["image"])

    img_data = requests.get(parsed["image"]).content
    local_image_path = "output/images/{}".format(os.path.basename(parsed["image"]))
    with open(local_image_path, "wb") as handler:
        handler.write(img_data)

    text = parsed["articleBody"]

    paragraphs = [
        Paragraph(
            header=None,
            image_path=None,
            text=paragraph,
        )
        for paragraph in text.split("\n")
    ]

    return Article(
        title=parsed["headline"],
        description=parsed["description"],
        paragraphs=[
            Paragraph(
                header=None,
                image_path=local_image_path.strip("output/"),
                text=None,
            ),
            *paragraphs,
        ],
    )


class Economist(NewsSource):
    def get_latest(self) -> Issue:
        date = "2023-07-29"

        sections = scrape_toc(date)
        issue = Issue(
            title="Economist {}".format(date),
            sections=[
                Section(
                    title=section.title,
                    articles=[
                        _parse_and_scrape(article)
                        for article in section.articles
                        if not article.link.startswith("/interactive")
                    ],
                )
                for section in sections
                if section.title != "Economic & financial indicators"
                and section.title != "Graphic detail"
            ],
        )

        return issue
