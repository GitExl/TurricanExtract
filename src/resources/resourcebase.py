class ResourceBase:

    TYPE = ''

    def __init__(self, name: str):
        self._name: str = name

    @property
    def name(self) -> str:
        return self._name
