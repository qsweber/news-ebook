from collections import namedtuple


_Article = namedtuple(
    '_Article',
    (
        'title',
        'intro',
        'paragraphs',
    )
)

_Paragraph = namedtuple(
    '_Paragraph',
    (
        'bold',
        'text',
    )
)


def get_article_html_id(section_html_id, index):
    return section_html_id + '_{}'.format(index)


def new_article(title, intro, paragraphs):
    return _Article(
        title=title,
        intro=intro,
        paragraphs=paragraphs,
    )


def new_paragraph(bold, text):
    return _Paragraph(bold, text)


def paragraph_as_html(paragraph):
    if paragraph.bold:
        bold_start = '<b>'
        bold_end = '</b>'
    else:
        bold_start = ''
        bold_end = ''

    return '<p>{bold_start}{text}{bold_end}</p>\n'.format(
        bold_start=bold_start,
        text=paragraph.text,
        bold_end=bold_end,
    )


def article_as_html(article, html_id):
    html_output = '<div class="article"><h3 id="{}">{}</h3>\n'.format(
        html_id,
        article.title,
    )
    if article.intro:
        html_output += '<h4>{}</h4>\n'.format(article.intro)

    html_output += ''.join([
        paragraph_as_html(paragraph)
        for paragraph in article.paragraphs
    ])

    html_output += "</div>"

    return html_output
