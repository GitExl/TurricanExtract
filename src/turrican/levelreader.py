from typing import List

from renderlib.stream_read import StreamRead
from resources.levelresource import Entity, LevelResource
from resources.tilesetresource import TileSetResource
from turrican.entityinfo import EntityInfoList
from turrican.tilemap import Tilemap


class LevelReaderBase:

    def __init__(self, stream: StreamRead, level: LevelResource):
        self._stream: StreamRead = stream
        self._level: LevelResource = level

    def read_tilemap(self, offset=0):
        pass

    def read_entities(self, entity_info_list: EntityInfoList):
        pass

    @property
    def level(self) -> LevelResource:
        return self._level


class TurricanBinaryLevelReader(LevelReaderBase):

    def __init__(self, stream: StreamRead, level: LevelResource, base_offset: int):
        super().__init__(stream, level)

        self._base_offset: int = base_offset

        self._offset_level_data: int = stream.read_uint() - self._base_offset

        self._tilemap_width: int = stream.read_ushort()
        self._tilemap_height: int = stream.read_ushort()

        level.camera_tile_x = stream.read_short() + 1
        level.camera_tile_y = stream.read_short() + 1

        level.player_x = stream.read_short() - 32
        level.player_y = stream.read_short() - 32

        self._blockmap_width: int = stream.read_ushort() + 1
        self._blockmap_height: int = stream.read_ushort() + 1

        # Pointers to code, relative to base offset.
        stream.read_uint()
        stream.read_uint()

        # Unknown
        stream.skip(4)

        # Pointer to offsets to enemy behaviour code, relative to base offset.
        stream.read_uint()

        self._offset_blockmap_row_pointers: int = stream.read_uint() - self._base_offset
        self._offset_blockmap_pointers: int = stream.read_uint() - self._base_offset

        level.subsong = stream.read_ushort()

        # Pointer to code, relative to base offset.
        stream.read_uint()

    def read_tilemap(self, offset: int = 0):
        self._stream.seek(self._offset_level_data + offset)
        self._level.tilemap = Tilemap.from_stream(self._stream, self._tilemap_width, self._tilemap_height)

    def read_entities(self, entity_info_list: EntityInfoList):
        row_offsets = [0] * self._blockmap_height
        self._stream.seek(self._offset_blockmap_row_pointers)
        for row_index in range(0, self._blockmap_height):
            row_offsets[row_index] = self._stream.read_ushort()

        block_y = 0
        for row_offset in row_offsets:

            # Read row offsets to blockmap block data.
            block_offsets = [0] * self._blockmap_width
            self._stream.seek(self._offset_blockmap_pointers + row_offset)
            for offset_index in range(0, self._blockmap_width):
                block_offsets[offset_index] = self._stream.read_uint() - self._base_offset

            # Each block contains a list of entities that are inside it.
            block_x = 0
            for offset_index, offset in enumerate(block_offsets):
                self._stream.seek(offset)
                self._level.entities.extend(self.read_entity_list(self._stream, entity_info_list, block_x, block_y))

                block_x += 1

            block_y += 1

    def read_entity_list(self, stream: StreamRead, entity_info_list: EntityInfoList, block_x: int, block_y: int) -> List[Entity]:
        pass
    
    @property
    def offset_level_data(self) -> int:
        return self._offset_level_data


class Turrican1LevelReader(TurricanBinaryLevelReader):

    def read_entity_list(self, stream: StreamRead, entity_info_list: EntityInfoList, block_x: int, block_y: int) -> List[Entity]:
        entities: List[Entity] = []

        while True:
            entity_type = stream.read_ubyte()
            entity_data = stream.read_ubyte()
            if entity_type == 0x00:
                break

            entity_subtype = entity_data & 0xF

            x = (stream.read_ushort() - 4) * 8
            y = stream.read_ushort() * 8

            entity_info = entity_info_list.get_info(entity_type, entity_subtype)
            if entity_info is None:
                print('No entity info for type {}, subtype {}.'.format(entity_type, entity_subtype))
                continue
            entity = Entity(entity_info, x, y)

            # TODO read and use from game config
            # Turrican 1 world 2 has everything shifted 32 pixels down...
            # if self._world_index == 1:
            #     entity.y += 4

            entities.append(entity)

        return entities


class Turrican2LevelReader(TurricanBinaryLevelReader):

    def read_entity_list(self, stream: StreamRead, entity_info_list: EntityInfoList, block_x: int, block_y: int) -> List[Entity]:
        entities: List[Entity] = []

        while True:
            value = stream.read_ubyte()
            if value == 0xFF:
                break

            entity_type = value & 0xF
            entity_subtype = (value >> 4) & 0xF

            x = (stream.read_ubyte() + block_x * 32 - 3) * 8
            y = (stream.read_ubyte() + block_y * 32) * 8

            entity_info = entity_info_list.get_info(entity_type, entity_subtype)
            if entity_info is None:
                print('No entity info for type {}, subtype {}.'.format(entity_type, entity_subtype))
                continue
            entity = Entity(entity_info, x, y)

            entities.append(entity)

        return entities
