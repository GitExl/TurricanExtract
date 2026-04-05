from enum import Enum
from typing import List, Optional, Iterator, Tuple

from renderlib.stream_read import StreamRead
from renderlib.surface import Surface
from resources.tilesetresource import TileSetResource


TileIndex = Optional[int]


class TileSurface(Enum):
    NORMAL = 0
    COLLISION = 1
    SECRET = 2


class Tilemap:

    TILE_SIZE = 32

    def __init__(self, tiles, width, height):
        self._tiles: List[TileIndex] = tiles
        self._width: int = width
        self._height: int = height

    @classmethod
    def from_stream(cls, stream: StreamRead, width: int, height: int):
        tiles = [None] * width * height

        for x in range(0, width):
            for y in range(0, height):
                tiles[x + y * width] = stream.read_ubyte()

        return cls(tiles, width, height)

    @classmethod
    def from_tilemap(cls, other, x1: int, y1: int, x2: int, y2: int):
        other_tiles = other.tiles

        width = x2 - x1
        height = y2 - y1
        tiles = [None] * width * height

        for y in range(y1, y2):
            for x in range(x1, x2):
                if x < 0 or x >= other.width:
                    continue
                if y < 0 or y >= other.height:
                    continue

                tiles[(x - x1) + (y - y1) * width] = other_tiles[x + y * other.width]

        return cls(tiles, width, height)

    def find(self, find: TileIndex) -> Iterator[Tuple[int, int, int]]:
        for index, tile in enumerate(self._tiles):
            if tile == find:
                yield index, index % self._width, index // self._width

    def replace(self, find: int, replace: int):
        for index, tile in enumerate(self._tiles):
            if tile == find:
                self._tiles[index] = replace

    def filter(self, keep: List[int]):
        for index, tile in enumerate(self._tiles):
            if tile not in keep:
                self._tiles[index] = None

    def render(self, surface: Surface, tileset: TileSetResource, tile_surface: TileSurface = TileSurface.NORMAL, tileset_alt: Optional[TileSetResource] = None, tileset_alt_y: Optional[int] = None):
        start_x: int = 0
        start_y: int = 0
        end_x: int = self._width
        end_y: int = self._height

        for y in range(start_y, end_y):
            if tileset_alt is not None and tileset_alt_y is not None and y * Tilemap.TILE_SIZE == tileset_alt_y:
                tileset = tileset_alt

            for x in range(start_x, end_x):
                offset = x + y * self._width
                if offset >= len(self._tiles):
                    continue
                    
                index = self._tiles[offset]
                if index is None or index >= len(tileset.tiles):
                    continue

                tile = tileset.tiles[index]
                tile_x = x * Tilemap.TILE_SIZE
                tile_y = y * Tilemap.TILE_SIZE
                if tile_surface == TileSurface.COLLISION:
                    surface.blit(tile.surface_collision, tile_x, tile_y)
                elif tile_surface == TileSurface.SECRET:
                    surface.blit(tile.surface_secret, tile_x, tile_y)
                else:
                    surface.blit(tile.surface, tile_x, tile_y)

    def put_from(self, other, put_x: int, put_y: int):
        other_tiles = other.tiles

        for y in range(0, other.height):
            for x in range(0, other.width):
                if put_x + x < 0 or put_y + y < 0:
                    continue
                if put_x + x >= self._width or put_y + y >= self._height:
                    continue

                source = x + y * other.width
                destination = put_x + x + (put_y + y) * self._width
                self._tiles[destination] = other_tiles[source]

    def put(self, index: int, tile_index: TileIndex):
        self._tiles[index] = tile_index

    def fill_with(self, other, x1: int, y1: int, x2: int, y2: int):
        other_tiles: List[TileIndex] = other.tiles
        other_x: int = 0
        other_y: int = 0

        for y in range(y1, y2):
            for x in range(x1, x2):
                if not (x < 0 or y < 0 or x >= self._width or y >= self._height):
                    source = other_x + other_y * other.width
                    destination = x + y * self._width
                    self._tiles[destination] = other_tiles[source]

                other_x += 1
                if other_x >= other.width:
                    other_x = 0

            other_x = 0
            other_y += 1
            if other_y >= other.height:
                other_y = 0

    def clear(self):
        self._width = 0
        self._height = 0
        self._tiles = []

    @property
    def tiles(self) -> List[TileIndex]:
        return self._tiles

    @tiles.setter
    def tiles(self, tiles: List[TileIndex]):
        self._tiles = tiles

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height
