import news_ebook.economist_kindle as module


def test_get_issue_title():
    issue_url = 'test/2015-01-23'
    expected = 'Week of January 23, 2015'
    actual = module._get_issue_title(issue_url)

    assert actual == expected
