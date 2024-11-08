import os
import typing

import json
import requests
from bs4 import BeautifulSoup
import typing

from news_ebook.clients.economist import EconomistClient
from news_ebook.lib.soup import find_tag, find_tags
from news_ebook.lib.news_source import Paragraph, Article, Section, Issue, NewsSource


class TocArticle(typing.NamedTuple):
    title: str
    link: str


class TocSection(typing.NamedTuple):
    title: str
    articles: typing.List[TocArticle]


# pylint: disable=too-few-public-methods
class Economist(NewsSource):
    def __init__(
        self, economist_client: EconomistClient, output_dir: str, issueDate: str
    ):
        self.economist_client = economist_client
        self.output_dir = output_dir
        self.issueDate = issueDate

    def get_latest(self) -> Issue:
        sections = self._scrape_toc(self.economist_client, self.issueDate)
        issue = Issue(
            title=f"Economist {self.issueDate}",
            sections=[
                Section(
                    title=section.title,
                    articles=[
                        a
                        for a in [
                            self._parse_and_scrape(self.economist_client, article)
                            for article in section.articles
                            if not article.link.startswith("/interactive")
                        ]
                        if a
                    ],
                )
                for section in sections
                if section.title
                not in (
                    "Economic & financial indicators",
                    "Graphic detail",
                    "The world this week",
                )
            ],
        )

        return issue

    def _scrape_toc(
        self, economist_client: EconomistClient, date: str
    ) -> typing.List[TocSection]:
        issue_url = "/printedition/{}".format(date)

        issue_soup = BeautifulSoup(
            economist_client.get_url(issue_url).text, "html.parser"
        )

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

    def _get_image_paragraph(self, element: typing.Any) -> Paragraph:
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
        img = self.economist_client.get_img(element["url"])
        desired_width = 600
        resized_height = int(
            (float(img.size[1]) * float(desired_width / float(img.size[0])))
        )
        img.thumbnail((desired_width, resized_height))
        basename = os.path.join(self.output_dir, "images")
        os.makedirs(basename, exist_ok=True)
        filename = os.path.basename(element["url"])
        small_local_image_path = f"{basename}/small-{filename}"
        img.save(small_local_image_path)

        return Paragraph(
            header=None,
            image_path=small_local_image_path.strip(f"{self.output_dir}/"),
            text=None,  # Can I do alt-text?
            blockquote=None,
        )

    def _get_paragraph(self, element: typing.Any) -> typing.Optional[Paragraph]:
        if not element or not element["type"]:
            print("can not find: {}", json.dumps(element))
            return None

        if element["type"] == "IMAGE":
            return self._get_image_paragraph(element)
        elif element["type"] == "PARAGRAPH":
            """
            {
                'type': 'PARAGRAPH',
                'text': 'Foo bar',
                'textHtml': '<p>Foo bar</p>'
            }
            """
            return Paragraph(
                header=None, blockquote=None, image_path=None, text=element["text"]
            )
        elif element["type"] == "CROSSHEAD":
            """
            {
                "type": "CROSSHEAD",
                "text": "A new competition",
                "__typename": "CrossheadComponent"
            }
            """
            return Paragraph(
                header=element["text"],
                image_path=None,
                text=None,
                blockquote=None,
            )
        elif element["type"] == "BLOCK_QUOTE":
            """
            {
                "type":"BLOCK_QUOTE",
                "text":"test quote",
                "textHtml":"\u003ci\u003etest quote\u003c/i\u003e",
                "__typename":"BlockQuoteComponent"
            }
            """
            return Paragraph(
                header=None, image_path=None, blockquote=element["text"], text=None
            )
        elif element["type"] == "INFOBOX":
            return None
        elif element["type"] == "INFOGRAPHIC":
            return None
        elif element["type"] == "PULL_QUOTE":
            return None
        elif element["type"] == "BOOK_INFO":
            return None

        print("can not parse: {}", json.dumps(element))
        return None

    def _parse_and_scrape(
        self, economist_client: EconomistClient, article: TocArticle
    ) -> typing.Optional[Article]:
        print(f"Scraping {article.link}")
        article_soup = BeautifulSoup(
            economist_client.get_url(article.link).text, "html.parser"
        )

        tag = None
        try:
            tag = find_tag(article_soup, "script", {"id": "__NEXT_DATA__"})
        except ValueError:
            print("no __NEXT_DATA__ tag found")
            return None

        parsed = json.loads(tag.text)
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
            paragraphs=[
                p for p in [self._get_paragraph(element) for element in elements] if p
            ],
        )
