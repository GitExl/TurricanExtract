from typing import List, Optional, Dict

from resources.resourcebase import ResourceBase
from turrican.tilemap import Tilemap
from turrican.entityinfo import EntityInfo


class Entity:

    def __init__(self, info: EntityInfo, x: int, y: int):
        self.info = info
        self.x: int = x
        self.y: int = y

    def __repr__(self):
        return '{} {} / {} @ {}x{}'.format(self.info.category, self.info.name, self.info.key, self.x, self.y)


class LevelResource(ResourceBase):

    TYPE = 'level'

    def __init__(self, name: str, title: str, world_index: int, level_index: int, data: Dict[str,any]):
        super().__init__(name)

        self.title: str = title
        self.world_index: int = world_index
        self.level_index: int = level_index

        self.tilemap: Optional[Tilemap] = None
        self.tileset: str = 'world{:02}'.format(self.world_index + 1)

        self.entities: List[Entity] = []

        self.subsong: int = 0

        self.camera_tile_x: int = 0
        self.camera_tile_y: int = 0

        self.player_x: int = 0
        self.player_y: int = 0

        self.alternate_tile_palette_y: Optional[int] = data.get('alternateTilePaletteY', None)
