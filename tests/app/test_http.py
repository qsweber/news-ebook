import json

import pytest

import news_ebook.app.http as module  # type: ignore


@pytest.fixture
def client():
    client = module.app.test_client()

    yield client


def test_status(mocker, client):
    result = client.get("/api/v0/status")

    print(result.text)
    assert result.status_code == 200
    assert json.loads(result.data) == {"text": "ok"}
