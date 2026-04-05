from typing import Dict

from environment import Environment
from renderlib.stream_read import StreamRead
from resources.resourcelist import ResourceList


class LoaderBase:

    TYPE = ''

    def __init__(self, resources: ResourceList):
        self._resources: ResourceList = resources

    def load(self, stream: StreamRead, options: Dict, environment: Environment):
        pass
