from neomodel import StringProperty

from estuary.models.base import EstuaryStructuredNode


class ProductVersion(EstuaryStructuredNode):
    """Definition of Product Version in Neo4j."""

    name = StringProperty(unique_index=True)
