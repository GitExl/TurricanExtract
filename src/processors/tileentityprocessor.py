import json
from pathlib import Path
from typing import List

from environment import Environment
from processors.processorbase import ProcessorBase
from resources.levelresource import LevelResource, Entity
from resources.resourcelist import ResourceList
from turrican.tilemap import Tilemap
from turrican.entityinfo import EntityInfo


class TileEntityProcessor(ProcessorBase):

    def process(self, environment: Environment, resources: ResourceList):
        with open(environment.path_game / Path('tile_entities.json'), 'r') as f:
            tile_entities = json.load(f)

        for level in resources.get_of_type(LevelResource.TYPE):
            tileset: str = level.tileset
            if tileset not in tile_entities:
                continue

            new_entities: List[Entity] = []

            for tile_index, tile_data in tile_entities[tileset].items():
                tile_index = int(tile_index)
                replace = tile_data.get('replace', None)

                tilemap: Tilemap = level.tilemap
                for index, tile_x, tile_y in tilemap.find(tile_index):
                    if replace is not None:
                        tilemap.put(index, replace)

                    for entity in tile_data['entities']:
                        info = EntityInfo(entity)
                        entity_x, entity_y = entity['position']

                        entity_x += (tile_x * Tilemap.TILE_SIZE)
                        entity_y += (tile_y * Tilemap.TILE_SIZE)

                        new_entities.append(Entity(info, entity_x, entity_y))

            level.entities = new_entities + level.entities
