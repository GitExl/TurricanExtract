import binascii
import json
from math import ceil
from pathlib import Path
from typing import cast

from environment import Environment
from resources.resourcebase import ResourceBase
from resources.tilesetresource import TileSetResource, CollisionType
from writers.writerbase import WriterBase


class TileSetWriter(WriterBase):

    TYPE = TileSetResource.TYPE

    def write(self, resource: ResourceBase, environment: Environment):
        tileset: TileSetResource = cast(TileSetResource, resource)

        tiles_info = []
        for tile_index, tile in enumerate(tileset.tiles):
            tile_collision = bytearray([0] * 16)
            for index, item in enumerate(tile.collision):
                if item == CollisionType.SOLID.value:
                    tile_collision[index] = 0x01
                elif item == CollisionType.DESTRUCTABLE.value:
                    tile_collision[index] = 0x02
                elif item == CollisionType.HURT.value:
                    tile_collision[index] = 0x04

            tiles_info.append({
                'id': tile_index + 1,
                'properties': [
                    {
                        'name': 'collision',
                        'type': 'string',
                        'value': binascii.hexlify(tile_collision).decode('ascii'),
                    },
                ],
            })

        layout = tileset.surface_list.get_layout()
        tile_width, tile_height = layout.frame_max_size

        data = {
            'columns': 10,
            'firstgid': 1,
            'image': '../textures/{}/tiles.png'.format(tileset.name),
            'imageheight': int(ceil(len(tileset.tiles) % 10)),
            'imagewidth': 320,
            'tilecount': len(tileset.tiles),
            'tilewidth': tile_width,
            'tileheight': tile_height,
            'tiles': tiles_info,
        }

        # Merge in tile animation data.
        merge_data_path = environment.path_game / Path('tilesets/{}.json'.format(tileset.name))
        if merge_data_path.exists():
            with open(merge_data_path, 'r') as f:
                marge_data = json.load(f)
            data.update(marge_data)

        filename = environment.path_output / Path('tilesets/{}.json'.format(tileset.name))
        print(filename)
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
