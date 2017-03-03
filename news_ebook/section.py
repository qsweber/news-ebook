from collections import namedtuple

from news_ebook.article import article_as_html, get_article_html_id

_Section = namedtuple(
    '_Section',
    (
        'title',
        'articles',
    )
)


def new_section(title, articles):
    return _Section(title, articles)


def section_as_html(section):
    section_html_id = get_section_html_id(section)

    html_output = '<div class="section"><h2 id="{}">{}</h2>\n'.format(section_html_id, section.title)

    html_output += ''.join([
        article_as_html(article, get_article_html_id(section_html_id, index))
        for index, article in enumerate(section.articles)
    ])

    html_output += '</div>\n'

    return html_output


def get_section_html_id(section):
    return '_'.join(section.title.split())
