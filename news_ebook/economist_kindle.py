import argparse
import datetime
import functools
import os
import requests

from bs4 import BeautifulSoup

from news_ebook.article import new_article, new_paragraph
from news_ebook.issue import new_issue, issue_as_html
from news_ebook.section import new_section

SECTIONS_TO_EXCLUDE = [
    'Economic and financial indicators',
]

BASE_URL = 'http://www.economist.com'


def _get_auth():
    if 'ECONOMIST_USERNAME' not in os.environ:
        with open('/vagrant/news-ebook/.pass', 'r') as fh:
            lines = fh.readlines()
            os.environ['ECONOMIST_USERNAME'] = lines[0].strip()
            os.environ['ECONOMIST_PASSWORD'] = lines[1].strip()

    return (os.environ['ECONOMIST_USERNAME'], os.environ['ECONOMIST_PASSWORD'])


def _get_complete_url(url):
    if not url.startswith(BASE_URL):
        url = os.path.join(BASE_URL, url.lstrip('/'))

    return url


@functools.lru_cache()
def _get_soup_for_url(url):
    complete_url = _get_complete_url(url)
    foo = requests.get(
        complete_url,
        headers={'User-Agent': 'Mozilla/5.0'},
        auth=_get_auth()
    )

    return BeautifulSoup(foo.text, "html.parser")


def _get_article_from_url(url):
    soup = _get_soup_for_url(url)
    article_soup = soup.find('body').find('article')

    headers = [
        child.text
        for child in article_soup.find_next(
            'h1',
            {'class': 'flytitle-and-title__body'}
        ).children
    ]

    if len(headers) in [1, 2]:
        title = ': '.join(headers)
    else:
        raise Exception('headers have new formatting')

    intro = article_soup.find_next('p', {'class': 'blog-post__rubric'})
    if intro:
        intro = intro.text
    else:
        intro = ''

    paragraphs = [
        new_paragraph(
            'xhead' in paragraph.attrs.get('class', []),
            paragraph.text
        )
        for paragraph in article_soup.find_next(
            'div',
            {'class': 'blog-post__text'},
        ).findAll('p')
    ]

    return new_article(title, intro, paragraphs)


def _get_section_from_soup(soup):
    title = soup.find_next('div').text

    if title in SECTIONS_TO_EXCLUDE:
        return None

    articles = [
        _get_article_from_url(item.attrs['href'])
        for item in soup.findAll('a')
    ]

    return new_section(title, articles)


def _get_issue_title(issue_url):
    return 'Week of {}'.format(datetime.datetime.strptime(
        os.path.basename(issue_url),
        '%Y-%m-%d',
    ).strftime('%B %d, %Y'))


def _get_issue_from_url(issue_url):
    soup = _get_soup_for_url(issue_url)

    sections = [
        _get_section_from_soup(section_soup)
        for section_soup in soup.find('body').find(
            'div',
            {'class': 'main-content__main-column print-edition__content'},
        ).find_next('ul').findAll('li', {'class': 'list__item'})
    ]

    sections = [section for section in sections if section]

    title = _get_issue_title(issue_url)

    return new_issue(title, sections)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--week', required=True)
    cli_args = parser.parse_args()

    issue_url = os.path.join(BASE_URL, 'printedition/{}'.format(
        cli_args.week,
    ))

    issue = _get_issue_from_url(issue_url)

    html_output = issue_as_html(issue)

    with open('/vagrant/Economist: {}.html'.format(issue.title), 'w') as fh:
        fh.write(html_output)
