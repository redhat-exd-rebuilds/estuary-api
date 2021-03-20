import json

import pytest
import requests
from estuary.models.bugzilla import BugzillaBug


@pytest.mark.parametrize("id", [("11111")])
def test_load_BugzillaBug(id):
    BugzillaBug.get_or_create({"id_": id})
    payload = {
        "statements": [
            {
                "statement": "MATCH (node:BugzillaBug) RETURN node.id",
                "parameters": {},
            },
        ]
    }
    headers = {
        "Accept": "application/json;charset=UTF-8",
        "Content-Type": "application/json",
    }
    response = requests.post(
        url="http://localhost:7474/db/neo4j/tx",
        headers=headers,
        data=json.dumps(payload),
    )
    assert response.status_code == 201
    assert response.json()["results"][0]["data"][0]["row"][0] == id
