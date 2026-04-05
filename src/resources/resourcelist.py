from typing import Dict, Optional, ValuesView, Iterable

from resources.resourcebase import ResourceBase


class ResourceList:

    def __init__(self):
        self._resources: Dict[str, ResourceBase] = {}

    def get(self, type: str, name: str) -> Optional[ResourceBase]:
        return self._resources.get('{}:{}'.format(type, name), None)

    def get_of_type(self, type: str) -> Iterable[ResourceBase]:
        for resource in self._resources.values():
            if resource.TYPE == type:
                yield resource

    def put(self, resource: ResourceBase):
        self._resources['{}:{}'.format(resource.TYPE, resource.name)] = resource

    @property
    def resources(self) -> ValuesView[ResourceBase]:
        return self._resources.values()
