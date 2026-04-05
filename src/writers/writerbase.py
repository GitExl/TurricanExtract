from environment import Environment
from resources.resourcebase import ResourceBase
from resources.resourcelist import ResourceList


class WriterBase:

    TYPE = ''

    def __init__(self, resources: ResourceList):
        self._resources: ResourceList = resources

    def write(self, resource: ResourceBase, environment: Environment):
        pass
