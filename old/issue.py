from collections import namedtuple

from bs4 import BeautifulSoup
from unidecode import unidecode

from news_ebook.section import section_as_html


_Issue = namedtuple(
    '_Issue',
    (
        'title',
        'sections',
    )
)


def new_issue(title, sections):
    return _Issue(title, sections)


def issue_as_html(issue):
    html_output = '<h1>{}</h1>\n'.format(issue.title)

    html_output += ''.join([
        section_as_html(section)
        for section in issue.sections
    ])

    soup = BeautifulSoup(html_output, "html.parser")

    toc = [(
        (
            section_html.find('h2').attrs['id'],
            section_html.find('h2').text,
        ), [
            (
                article_html.find('h3').attrs['id'],
                article_html.find('h3').text,
            )
            for article_html in section_html.findAll(
                'div',
                {'class': 'article'},
            )
        ])
        for section_html in soup.findAll('div', {'class': 'section'})
    ]

    toc_html = '<ul>'
    for section, articles in toc:
        section_id, section_title = section
        toc_html += '<li><a href=#{}>{}</a><ul>'.format(
            section_id,
            section_title,
        )
        for article_id, article_title in articles:
            toc_html += '<li><a href="#{}">{}</a></li>'.format(
                article_id,
                article_title,
            )
        toc_html += '</ul></li>'
    toc_html += '</ul>'

    return unidecode('<!DOCTYPE html><html><body>{}{}</body></html>'.format(
        toc_html,
        html_output
    ))
