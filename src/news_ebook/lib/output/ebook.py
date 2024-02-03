import os

from news_ebook.lib.news_source import Issue
from ebooklib import epub  # type: ignore
from news_ebook.lib.output import Output as BaseOutput


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
        all_chapters = []
        image_counter = 1
        for section in issue.sections:
            chapters = []
            for article in section.articles:
                chapter = epub.EpubHtml(
                    title=article.title,
                    file_name="{}.xhtml".format(article.title),
                    lang="en",
                )
                content = "<h1>{}</h1>".format(article.title)
                for paragraph in article.paragraphs:
                    if paragraph.text:
                        content += "<p>{}</p>".format(paragraph.text)
                    elif paragraph.image_path:
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
            foo = (epub.Section(section.title), tuple(chapters))
            sections.append(foo)

        book.toc = tuple(sections)

        # add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # basic spine
        book.spine = ["nav", *all_chapters]

        # write to the file
        output_file_name = "{}.epub".format(issue.title)
        epub.write_epub(output_file_name, book, {})

        return output_file_name
