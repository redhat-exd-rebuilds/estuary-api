import json

import pytest
import requests
from estuary.models.bugzilla import BugzillaBug


@pytest.mark.parametrize("id", [("11111"), ("22222")])
def test_load_BugzillaBug(id):
    BugzillaBug.get_or_create({"id_": id})
    payload = {
        "query": "MATCH (node:BugzillaBug) WHERE node.id = {id} RETURN node.id",
        "params": {
            "id": id
        },
    }
    headers = {
        "Accept": "application/json;charset=UTF-8",
        "Content-Type": "application/json",
    }
    response = requests.post(
        url="http://localhost:7474/db/data/cypher",
        headers=headers,
        data=json.dumps(payload),
    )
    assert response.status_code == 200
    assert response.json()["data"][0][0] == id
