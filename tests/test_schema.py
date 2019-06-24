"""Schema tests."""

import pytest

from docknv.schema import SchemaCollection, MissingSchema, MalformedSchema

from docknv.utils.serialization import yaml_ordered_load


def test_schema():
    """Schema."""
    schema_def = """\
standard:
    volumes:
        - portainer
    services:
        - portainer
    networks:
        - net

standard2:
    includes:
        - standard
    services:
        - pouet
    networks:
        - net

hello:
    services:
        - hello-world\
    """

    # Load schemas
    schemas = SchemaCollection.load_from_data(yaml_ordered_load(schema_def))
    assert len(schemas) == 3

    # First schema
    first_schema = schemas.get_schema("standard2")
    assert first_schema.name == "standard2"
    assert len(first_schema.services) == 2
    assert len(first_schema.networks) == 1
    assert len(first_schema.volumes) == 1
    assert "portainer" in first_schema.services
    assert "pouet" in first_schema.services
    assert "net" in first_schema.networks
    assert "portainer" in first_schema.volumes

    # Should error
    with pytest.raises(MissingSchema):
        schemas.get_schema("standard3")

    assert schemas.includes_schema("standard")
    assert not schemas.includes_schema("standard3")

    # Show schemas
    schemas.show()


def test_schema_error():
    """Schema."""
    schema_def = """\
standard:
    volumes:
        - portainer
    services:
        - portainer
    networks:
        - net

standard2:
    includes:
        - standard3
    services:
        - pouet
    networks:
        - net

hello:
    services:
        - hello-world\
    """

    with pytest.raises(MalformedSchema):
        # Should error
        SchemaCollection.load_from_data(yaml_ordered_load(schema_def))
