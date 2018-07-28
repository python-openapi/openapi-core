"""OpenAPI core parameters generators module"""
from six import iteritems

from openapi_core.compat import lru_cache
from openapi_core.schema.parameters.factories import ParameterFactory


class ParametersGenerator(object):

    def __init__(self, dereferencer, schemas_registry):
        self.dereferencer = dereferencer
        self.schemas_registry = schemas_registry

    def generate(self, parameters):
        for parameter_name, parameter_spec in iteritems(parameters):
            parameter = self.parameter_factory.create(
                parameter_spec, parameter_name=parameter_name)

            yield (parameter_name, parameter)

    def generate_from_list(self, parameters_list):
        for parameter_spec in parameters_list:
            parameter = self.parameter_factory.create(parameter_spec)

            yield (parameter.name, parameter)

    @property
    @lru_cache()
    def parameter_factory(self):
        return ParameterFactory(self.dereferencer, self.schemas_registry)
