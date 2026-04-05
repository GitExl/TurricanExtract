from pathlib import Path
from typing import Dict, Optional, cast

from environment import Environment
from loaders.loaderbase import LoaderBase
from renderlib.stream_read import StreamRead
from resources.surfacelistresource import SurfaceListResource
from turrican.entityinfo import EntityInfoList, EntityInfo
from turrican.levelreader import Turrican1LevelReader, Turrican2LevelReader

from resources.tilesetresource import TileSetResource
from resources.levelresource import LevelResource, Entity


class TurricanWorldLoader(LoaderBase):

    TYPE = 'turrican_world'

    def load(self, stream: StreamRead, options: Dict, environment: Environment):
        base_offset = int(options.get('baseOffset'))
        world_index = int(options.get('index'))

        offset_tile_gfx = stream.read_uint() - base_offset
        offset_tile_collision = stream.read_uint() - base_offset
        offset_palette = stream.read_uint() - base_offset

        # The offset at which the MUS* files get loaded. sample data points to the start of the file,
        # music data points to the start of the music data in the file in memory.
        _offset_sample_data = stream.read_uint() - base_offset
        _offset_music_data = stream.read_uint() - base_offset

        if offset_tile_gfx > stream.size or offset_tile_collision > stream.size or offset_palette > stream.size:
            raise Exception('World file is not valid.')

        # Read level header offsets.
        level_count = stream.read_ushort()
        level_offsets = []
        for _ in range(0, level_count):
            level_offsets.append(stream.read_uint() - base_offset)

        # Read level headers.
        levels_info = options.get('levels')
        for level_index, level_info in enumerate(levels_info):
            stream.seek(level_offsets[level_index])

            level_name = 'world{:02}-level{:02}'.format(world_index + 1, level_index + 1)
            level = LevelResource(level_name, level_info.get('title'), world_index, level_index, level_info, options)

            version = options.get('version', 2)
            if version == 1:
                level_reader = Turrican1LevelReader(stream, level, base_offset)
            elif version == 2:
                level_reader = Turrican2LevelReader(stream, level, base_offset)
            else:
                raise Exception('Unknown world version.')

            level_file = level_info.get('file', None)
            if level_file is not None:
                level_file = environment.path_input / Path(level_file)
                stream.insert(str(level_file), level_reader.offset_level_data)

            tilemap_offset = level_info.get('tilemapOffset', 0)
            level_reader.read_tilemap(tilemap_offset)

            entity_info: EntityInfoList = EntityInfoList(environment.path_game, world_index, level_index)
            level_reader.read_entities(entity_info)

            # Create entities that are spawned through code.
            extra_entities = level_info.get('extraEntities', [])
            for extra_entity in extra_entities:
                info = EntityInfo({
                    'name': 'Extra',
                    'category': 'extra',
                    'key': extra_entity[0],
                })
                entity = Entity(info, extra_entity[1], extra_entity[2])
                level_reader.level.entities.append(entity)

            self._resources.put(level_reader.level)

        tile_surfaces_name = 'world{:02}/tiles'.format(world_index + 1)
        tile_surfaces: Optional[SurfaceListResource] = cast(SurfaceListResource, self._resources.get('surface_list', tile_surfaces_name))
        if tile_surfaces is None:
            raise Exception('Cannot find tile surfaces for world {}.'.format(world_index + 1))
        else:
            tileset_name = 'world{:02}'.format(world_index + 1)
            tileset = TileSetResource(tileset_name, tile_surfaces)
            tileset.read_collision(stream, offset_tile_collision)
            self._resources.put(tileset)

        # TODO
        # Duplicate the tileset in an alternate palette if needed.
        # if options.get('alternateTilePalette') is not None:
        #     stream.seek(options.get('alternateTilePalette'))
        #     palette_alt = Palette.from_stream(stream, 16, 4)
        #     mask_color = options.get('tileTransparentColor', None)
        #     tileset_alt = TileSet.from_stream(stream, offset_tile_gfx, palette_alt, mask_color)
