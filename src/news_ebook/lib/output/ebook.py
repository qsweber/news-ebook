import os
import re

from news_ebook.lib.news_source import Issue
from ebooklib import epub  # type: ignore
from news_ebook.lib.output import Output as BaseOutput

import typing


class Output(BaseOutput):
    def get_output_path(self, issue: Issue) -> str:
        book = epub.EpubBook()

        # set metadata
        book.set_identifier(issue.title)
        book.set_title(issue.title)
        book.set_language("en")

        book.add_author(
            "Quinn Weber",
        )

        sections = []
        all_chapters: typing.List[epub.EpubHtml] = []
        image_counter = 1
        for section in issue.sections:
            chapters = []
            for article in section.articles:
                chapter = epub.EpubHtml(
                    title=article.title,
                    file_name="{}.xhtml".format(
                        re.sub(r"\W+", "", article.title).lower()
                    ),
                    lang="en",
                )
                content = "<h1>{}</h1>".format(article.title)
                for paragraph in article.paragraphs:
                    if paragraph.header:
                        content += "<h4>{}</h4>".format(paragraph.header)
                    if paragraph.text:
                        content += "<p>{}</p>".format(paragraph.text)
                    if paragraph.image_path:
                        file_name = "static/{}".format(
                            os.path.basename(paragraph.image_path)
                        )
                        content += '<p><img src="{}"/></p>'.format(file_name)
                        image_content = open(
                            "output/{}".format(paragraph.image_path), "rb"
                        ).read()
                        img = epub.EpubImage(
                            uid="image_{}".format(image_counter),
                            file_name=file_name,
                            media_type="image/jpg",
                            content=image_content,
                        )
                        book.add_item(img)
                        image_counter += 1

                chapter.content = content
                book.add_item(chapter)
                chapters.append(chapter)
                all_chapters.append(chapter)

            sections.append((epub.Section(section.title), tuple(chapters)))

        # book.toc = tuple(sections)
        book.toc = tuple(
            epub.Link(chapter.file_name, chapter.title, chapter.title)
            for chapter in all_chapters
        )

        # add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # basic spine
        book.spine = ["nav", *all_chapters]

        # write to the file
        output_file_name = "{}.epub".format(issue.title)
        epub.write_epub(output_file_name, book, {})

        return output_file_name
