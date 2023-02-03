import argparse
import datetime
import functools
import os
import requests

import boto3
from bs4 import BeautifulSoup

from news_ebook.article import new_article, new_paragraph
from news_ebook.issue import new_issue, issue_as_html
from news_ebook.section import new_section

SECTIONS_TO_EXCLUDE = [
    'Economic and financial indicators',
]

BASE_URL = 'http://www.economist.com'


def _get_auth():
    return (
        os.environ['ECONOMIST_USERNAME'],
        os.environ['ECONOMIST_PASSWORD'],
    )


def _get_boto():
    return (
        os.environ['AWS_ACCESS_KEY_ID'],
        os.environ['AWS_SECRET_ACCESS_KEY'],
    )


def _get_email_address():
    return (
        os.environ['FROM_ADDRESS'],
        os.environ['TO_ADDRESS'],
    )


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
    parser.add_argument('--week', required=False)
    cli_args = parser.parse_args()

    if cli_args.week:
        week = cli_args.week
    else:
        today = datetime.date.today()
        if today.weekday() >= 4:
            week = today - datetime.timedelta(today.weekday()) + datetime.timedelta(5)
        else:
            week = today - datetime.timedelta(today.weekday()) - datetime.timedelta(2)

        week = week.strftime('%Y-%m-%d')

    issue_url = os.path.join(BASE_URL, 'printedition/{}'.format(week))

    print('Scraping {}'.format(issue_url))

    issue = _get_issue_from_url(issue_url)

    html_output = issue_as_html(issue)

    access_key_id, secret_access_key = _get_boto()
    client = boto3.client(
        'ses',
        region_name='us-west-2',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
    )

    from_address, to_address = _get_email_address()

    raw_message = '''From: {from_address}
To: {to_address}
Subject: doc
MIME-Version: 1.0
Content-type: Multipart/Mixed; boundary="NextPart"

--NextPart
Content-Type: text/plain

See attachment.

--NextPart
Content-Type: text/plain;
Content-Disposition: attachment; filename="{filename}"

{content}

--NextPart--'''.format(
        from_address=from_address,
        to_address=to_address,
        filename='Economist: {}.html'.format(issue.title),
        content=html_output
    )

    response = client.send_raw_email(
        Destinations=[
        ],
        RawMessage={'Data': raw_message.encode()},
    )

    return response
