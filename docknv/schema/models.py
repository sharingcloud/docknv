"""Schema models."""

import copy

from docknv.logger import Logger, Fore

from docknv.utils.serialization import yaml_merge


class MissingSchema(Exception):
    """Missing schema."""

    def __init__(self, schema):
        """Init."""
        message = f"Missing schema {schema}"
        super(MissingSchema, self).__init__(message)


class MalformedSchema(Exception):
    """Malformed schema."""

    def __init__(self, schema):
        """Init."""
        message = f"Malformed schema {schema}"
        super(MalformedSchema, self).__init__(message)


class Schema(object):
    """Schema."""

    def __init__(self, name, services=None, volumes=None, networks=None):
        """Init."""
        self.name = name
        self.services = services or []
        self.volumes = volumes or []
        self.networks = networks or []

    def show(self):
        """Show schema."""
        Logger.raw(f"- Schema: {self.name}", color=Fore.GREEN)
        if len(self.services) > 0:
            Logger.raw("  Services: ", color=Fore.BLUE)
            for service in self.services:
                Logger.raw(f"    - {service}")

        if len(self.volumes) > 0:
            Logger.raw("  Volumes: ", color=Fore.BLUE)
            for volume in self.volumes:
                Logger.raw(f"    - {volume}")

        if len(self.networks) > 0:
            Logger.raw("  Networks: ", color=Fore.BLUE)
            for network in self.networks:
                Logger.raw(f"    - {network}")


class SchemaCollection(object):
    """Schema collection."""

    def __init__(self, schemas):
        """Init."""
        self.schemas = schemas

    def __len__(self):
        return len(self.schemas)

    def get_schema(self, schema):
        """
        Get schema by name.

        :param schema:  Schema name (str)
        :rtype: Schema
        """
        if schema not in self.schemas:
            raise MissingSchema(schema)
        return self.schemas[schema]

    def includes_schema(self, schema):
        """
        Is schema included.

        :param schema:  Schema name (str)
        """
        return schema in self.schemas

    def resolve_schemas(self, schemas, services=None, volumes=None,
                        networks=None):
        """
        Resolve schemas.

        :param schemas:     Schema list (list)
        :param services:    Existing services (list?)
        :param volumes:     Existing volumes (list?)
        :param networks:    Networks (list?)

        :rtype: (Services, Volumes, Networks)
        """
        out_services = set(services if services else [])
        out_volumes = set(volumes if volumes else [])
        out_networks = set(networks if networks else [])

        for schema_name in schemas:
            schema = self.get_schema(schema_name)
            out_services.update(schema.services)
            out_volumes.update(schema.volumes)
            out_networks.update(schema.networks)

        return list(out_services), list(out_volumes), list(out_networks)

    @classmethod
    def load_from_data(cls, data):
        """
        Load from path.

        :param data:    Schema data (dict)
        :rtype: Schema collection
        """
        loaded_schemas = {}
        schema_cache = {}

        for key, schema_data in data.items():
            schema_copy = copy.deepcopy(schema_data)

            if "includes" in schema_data:
                includes = schema_data["includes"]
                included_schemas = []

                for include in includes:
                    if include not in schema_cache:
                        raise MalformedSchema(key)
                    included_schemas.append(schema_cache[include])

                del schema_copy["includes"]
                schema_copy = yaml_merge(included_schemas + [schema_copy])

            schema_cache[key] = schema_copy

        for key, schema_data in schema_cache.items():
            loaded_schemas[key] = Schema(
                key,
                services=schema_data.get("services", []),
                volumes=schema_data.get("volumes", []),
                networks=schema_data.get("networks", []))

        return cls(loaded_schemas)

    def show(self):
        """Show collection."""
        for schema in self.schemas.values():
            schema.show()
