import json

import pytest
import requests

from estuary.models.productversion import ProductVersion


@pytest.mark.parametrize("name", [("8.4.0.0"), ("8.5.0.0")])
def test_load_ProductVersion(name):
    ProductVersion.get_or_create({"name": name})
    payload = {
        "query": "MATCH (node:ProductVersion) WHERE node.name = {name} RETURN node.name",
        "params": {"name": name},
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
    assert response.json()["data"][0][0] == name
