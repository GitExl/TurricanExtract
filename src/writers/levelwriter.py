import base64
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
        for entity in level.entities:
            entity_data.append({
                'key': entity.info.key,
                'name': entity.info.name,
                'category': entity.info.category,
                'x': entity.x,
                'y': entity.y,
            })

        data = {
            'title': level.title,
            'layers': [
                {
                    'type': 'tile',
                    'width': level.tilemap.width,
                    'height': level.tilemap.height,
                    'tiles': base64.b64encode(bytes(level.tilemap.tiles)).decode('utf8'),
                    'tileset': level.tileset,
                    'parallax': {
                        'x': 0,
                        'y': 0,
                    }
                }
            ],
            'entities': entity_data,
            'camera': {
                'x': level.camera_tile_x * 32,
                'y': level.camera_tile_y * 32,
            },
            'music': {
                'source': 'world{:02}'.format(level.world_index + 1),
                'track': level.subsong,
            },
            'start': {
                'x': level.camera_tile_x * 32 + level.player_x,
                'y': level.camera_tile_y * 32 + level.player_y,
            }
        }

        filename = environment.path_output / Path('levels/world{:02}-level{:02}.json'.format(level.world_index + 1, level.level_index + 1))
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
