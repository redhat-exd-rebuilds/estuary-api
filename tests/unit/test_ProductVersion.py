import pytest

from estuary.models.productversion import ProductVersion


@pytest.mark.parametrize("name", [("8.4.0.0"), ("8.5.0.0")])
def test_ProductVersion(name):
    """Test ProductVersion."""
    productversion = ProductVersion(name=name).save()
    assert productversion.name == name
