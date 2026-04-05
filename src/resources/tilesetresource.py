from enum import Enum
from typing import List, Optional

from renderlib.stream_read import StreamRead
from renderlib.surface import Surface, BlendOp
from resources.resourcebase import ResourceBase
from resources.surfacelistresource import SurfaceListResource


class CollisionType(Enum):
    SOLID = 1
    DESTRUCTABLE = 127
    SECRET = 128
    HURT = 211


class Tile:

    def __init__(self):
        self.surface: Optional[Surface] = None
        self.surface_secret: Optional[Surface] = None
        self.surface_collision: Optional[Surface] = None

        self.collision: Optional[List[CollisionType]] = None

    def render_collision(self):
        self.surface_collision = Surface.empty(self.surface.width, self.surface.height)

        for index in range(0, 16):
            if not self.collision[index]:
                continue

            x = (index % 4) * 8
            y = int(index / 4) * 8

            value = self.collision[index]
            if value == CollisionType.SOLID.value:
                pass
            elif value == CollisionType.DESTRUCTABLE.value:
                color = 0xFF00FF00
                self.surface_collision.box_fill(x, y, 8, 8, color, BlendOp.SOLID)
            elif value == CollisionType.HURT.value:
                color = 0xFFFF0000
                self.surface_collision.box_fill(x, y, 8, 8, color, BlendOp.SOLID)
            elif value == CollisionType.SECRET.value:
                color = 0xFFFF00FF
                self.surface_collision.box_fill(x, y, 8, 8, color, BlendOp.SOLID)
            else:
                raise Exception('Unknown tile collision value {}.'.format(value))

    def render_secret(self):
        self.surface_secret = Surface.empty(self.surface.width, self.surface.height)

        for index in range(0, 16):
            if not self.collision[index]:
                continue

            x = (index % 4) * 8
            y = int(index / 4) * 8

            value = self.collision[index]
            if value == CollisionType.SECRET.value:
                self.surface_secret.box_fill(x, y, 8, 8, 0x88000000, BlendOp.SOLID)


class TileSetResource(ResourceBase):

    TYPE = 'tileset'

    def __init__(self, name: str, surface_list: SurfaceListResource):
        super().__init__(name)

        self.tiles: List[Tile] = []
        for surface in surface_list.surfaces:
            tile = Tile()
            tile.surface = surface
            self.tiles.append(tile)

        self.surface_list = surface_list

    def read_collision(self, stream: StreamRead, offset_collision: int):
        stream.seek(offset_collision)
        for tile in self.tiles:
            tile.collision = [0] * 16
            for index in range(0, 16):
                tile.collision[index] = stream.read_ubyte()
            tile.render_collision()
            tile.render_secret()
