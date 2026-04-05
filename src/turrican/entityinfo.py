import json
from pathlib import Path
from typing import Dict, Tuple, Optional


EntityInfoKey = Tuple[int, int]


class EntityInfo:

    def __init__(self, data: Dict[str, str]):
        self.category: str = data.get('category', 'none')
        self.name: str = data.get('name')
        self.key: str = data.get('key')
        self.gfx: Optional[str] = data.get('gfx', None)
        self.gfx_index: int = data.get('gfx_index', 0)


class EntityInfoList:

    def __init__(self, data_path: Path, world_index: int, level_index: int):
        self._info: Dict[EntityInfoKey, EntityInfo] = {}
        self._info.update(self._load_info_file(data_path / Path('entities/shared.json')))
        self._info.update(self._load_info_file(data_path / Path('entities/world{}-shared.json'.format(world_index + 1))))
        self._info.update(self._load_info_file(data_path / Path('entities/world{}-level{}.json'.format(world_index + 1, level_index + 1))))

    def get_info(self, type: int, subtype: int) -> Optional[EntityInfo]:
        return self._info.get((type, subtype), None)

    @staticmethod
    def _load_info_file(file_path: Path):
        info: Dict[EntityInfoKey, EntityInfo] = {}

        if not file_path.exists():
            return info

        with open(file_path, 'r') as fp:
            data = json.load(fp)

        for type_key, type_data in data.items():
            if 'type' not in type_data:
                raise Exception('Entity info for type {} has no type information.'.format(type_key))
            if 'subtypes' not in type_data:
                raise Exception('Entity info for type {} has no subtypes.'.format(type_key))

            type_key = int(type_key)
            info_data = type_data['type']

            for subtype_key, subtype_info_data in type_data['subtypes'].items():
                subtype_key = int(subtype_key)

                merged_info_data = info_data.copy()
                merged_info_data.update(subtype_info_data)

                info_key = (type_key, subtype_key)
                info[info_key] = EntityInfo(merged_info_data)

        return info
