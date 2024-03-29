from news_ebook.lib.news_source import Issue
from django.template import Engine, Context
from news_ebook.lib.output import Output as BaseOutput


engine = Engine(dirs=["src/news_ebook/lib/output/templates"])


class Output(BaseOutput):
    def get_output_path(self, issue: Issue) -> str:
        template = engine.get_template("basic.html")
        context = Context(
            {
                "title": issue.title,
                "sections": [
                    {
                        "title": section.title,
                        "id": "_".join(section.title.split()),
                        "articles": [
                            {
                                "title": article.title,
                                "id": "_".join(article.title.split()),
                                "paragraphs": [
                                    {
                                        "header": paragraph.header,
                                        "text": paragraph.text,
                                        "image_path": paragraph.image_path,
                                    }
                                    for paragraph in article.paragraphs
                                ],
                            }
                            for article in section.articles
                        ],
                    }
                    for section in issue.sections
                ],
            }
        )
        result = template.render(context)

        with open("output/economist.html", "w") as f:
            f.write(result)

        return "output/economist.html"
