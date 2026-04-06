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
            collision_objects = []
            x = 0
            y = 0
            for index, item in enumerate(tile.collision):
                if item == CollisionType.SOLID.value:
                    collision_objects.append({
                        'x': x,
                        'y': y,
                        'width': 8,
                        'height': 8,
                        'opacity': 1.0,
                        'type': 'solid',
                        'visible': True,
                    })
                elif item == CollisionType.DESTRUCTABLE.value:
                    collision_objects.append({
                        'x': x,
                        'y': y,
                        'width': 8,
                        'height': 8,
                        'opacity': 1.0,
                        'type': 'destructable',
                        'visible': True,
                    })
                elif item == CollisionType.SECRET.value:
                    collision_objects.append({
                        'x': x,
                        'y': y,
                        'width': 8,
                        'height': 8,
                        'opacity': 1.0,
                        'type': 'secret',
                        'visible': True,
                    })
                elif item == CollisionType.HURT.value:
                    collision_objects.append({
                        'x': x,
                        'y': y,
                        'width': 8,
                        'height': 8,
                        'opacity': 1.0,
                        'type': 'damage',
                        'visible': True,
                    })

                x += 8
                if x >= 32:
                    x = 0
                    y += 8

            tiles_info.append({
                'id': tile_index,
                'objectgroup': {
                    'type': 'objectgroup',
                    'draworder': 'index',
                    'name': 'collision',
                    'objects': collision_objects,
                    'opacity': 1.0,
                    'visible': True
                },
            })

        layout = tileset.surface_list.get_layout()
        tile_width, tile_height = layout.frame_max_size

        data = {
            'name': tileset.name,
            'columns': 10,
            'image': '../textures/{}/tiles.png'.format(tileset.name),
            'imageheight': int(ceil(len(tileset.tiles) % 10)),
            'imagewidth': 320,
            'tilecount': len(tileset.tiles),
            'tilewidth': tile_width,
            'tileheight': tile_height,
            'margin': 0,
            'spacing': 0,
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
