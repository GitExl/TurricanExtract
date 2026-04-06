import json
from pathlib import Path
from typing import cast

from environment import Environment
from resources.levelresource import LevelResource
from resources.resourcebase import ResourceBase
from writers.writerbase import WriterBase


class LevelWriter(WriterBase):

    TYPE = LevelResource.TYPE

    def write(self, resource: ResourceBase, environment: Environment):
        level: LevelResource = cast(LevelResource, resource)

        entity_data = []
        for index, entity in enumerate(level.entities):

            # Collect property data.
            props = []
            for key, value in entity.info.raw.items():
                if key in ['key', 'name', 'type', 'gfx', 'gfx_index', 'offset']:
                    continue
                if isinstance(value, str):
                    props.append({
                        'name': key,
                        'type': 'string',
                        'value': value,
                    })
                elif isinstance(value, int):
                    props.append({
                        'name': key,
                        'type': 'int',
                        'value': value,
                    })

            entity_data.append({
                'id': index,
                'type': entity.info.key,
                'name': entity.info.name,
                'x': entity.x,
                'y': entity.y,
                'properties': props,
            })

        # TilEd map data.
        data = {
            'version': '1',
            'orientation': 'orthogonal',
            'renderorder': 'right-down',
            'tilewidth': 32,
            'tileheight': 32,
            'width': level.tilemap.width,
            'height': level.tilemap.height,

            'properties': [
                {
                    'name': 'title',
                    'type': 'string',
                    'value': level.title,
                },
                {
                    'name': 'camera_x',
                    'type': 'int',
                    'value': level.camera_tile_x * 32,
                },
                {
                    'name': 'camera_y',
                    'type': 'int',
                    'value': level.camera_tile_y * 32,
                },
                {
                    'name': 'start_x',
                    'type': 'int',
                    'value': level.camera_tile_x * 32 + level.player_x,
                },
                {
                    'name': 'start_y',
                    'type': 'int',
                    'value': level.camera_tile_y * 32 + level.player_y,
                },
                {
                    'name': 'subsong',
                    'type': 'int',
                    'value': level.subsong,
                },
            ],

            'tilesets': [
                {
                    'firstgid': 1,
                    'source': '../tilesets/world{:02}.json'.format(level.world_index + 1),
                },
            ],
            'nextobjectid': len(entity_data),

            'layers': [
                {
                    'name': 'Tiles',
                    'type': 'tilelayer',
                    'width': level.tilemap.width,
                    'height': level.tilemap.height,
                    'data': list(map(lambda i: i + 1, level.tilemap.tiles)),
                    'visible': True,
                    'opacity': 1.0,
                },
                {
                    'name': 'Objects',
                    'type': 'objectgroup',
                    'objects': entity_data,
                    'visible': True,
                    'opacity': 1.0,
                },
            ],
        }

        filename = environment.path_output / Path('levels/world{:02}-level{:02}.json'.format(level.world_index + 1, level.level_index + 1))
        print(filename)
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
