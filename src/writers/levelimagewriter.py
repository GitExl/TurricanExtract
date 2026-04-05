import os
from pathlib import Path
from typing import Dict, Optional, cast

from environment import Environment
from renderlib.font import Font
from renderlib.surface import Surface, BlendOp
from resources.levelresource import LevelResource
from resources.resourcebase import ResourceBase
from resources.resourcelist import ResourceList
from resources.surfacelistresource import SurfaceListResource
from resources.tilesetresource import TileSetResource
from turrican.tilemap import Tilemap, TileSurface
from writers.writerbase import WriterBase


class LevelImageWriter(WriterBase):

    TYPE = LevelResource.TYPE

    ORIGIN_SIZE = 8

    COLOR_ORIGIN = 0xAA000000
    COLOR_BLOCKMAP = 0xFFFF00FF

    COLOR_CAMERA = 0xFFFFFF00
    COLOR_PLAYER = 0xFFFF0000

    CAMERA_WIDTH = 304
    CAMERA_HEIGHT = 192

    PLAYER_WIDTH = 32
    PLAYER_HEIGHT = 36

    COLOR_TEXT = 0xFFFFFFFF

    def __init__(self, resources: ResourceList):
        super().__init__(resources)

        self._font = Font.from_png('fonts/zepto.png')
        self._compression_level = 0

    def write(self, resource: ResourceBase, environment: Environment):
        level: LevelResource = cast(LevelResource, resource)
        tileset = cast(TileSetResource, self._resources.get(TileSetResource.TYPE, level.tileset))

        surfaces: Dict[str, Surface] = {}

        # Base tile layer. Without pickups or destructibles.
        surface_tiles = Surface.empty(level.tilemap.width * Tilemap.TILE_SIZE, level.tilemap.height * Tilemap.TILE_SIZE)
        bare_tilemap = Tilemap.from_tilemap(level.tilemap, 0, 0, level.tilemap.width, level.tilemap.height)

        # TODO
        # for pair in world.info.get('pickupTiles', []):
        #     bare_tilemap.replace(pair[0], pair[1])
        # for pair in world.info.get('destructibleTiles', []):
        #     bare_tilemap.replace(pair[0], pair[1])

        bare_tilemap.render(surface_tiles, tileset, TileSurface.NORMAL, tileset, level.alternate_tile_palette_y)
        self._paint_entities(level, surface_tiles, 'decor', False, False, False)
        surfaces['tiles'] = surface_tiles

        # Secrets. Secret entities and Turrican II secret flagged subtiles.
        surface_secrets = Surface.empty(level.tilemap.width * Tilemap.TILE_SIZE, level.tilemap.height * Tilemap.TILE_SIZE)

        # TODO: secret flagged tiles
        # if game_name == 'turrican2cdtv':
        #     level.tilemap.render(surface_secrets, world.tileset, TileSurface.SECRET, world.tileset_alt, level.alternate_tile_palette_y)

        self._paint_entities(level, surface_secrets, 'secret', False, False, False)
        surfaces['secrets'] = surface_secrets

        # Destructible.
        surface_destructible = Surface.empty(level.tilemap.width * Tilemap.TILE_SIZE, level.tilemap.height * Tilemap.TILE_SIZE)
        destructible_tilemap = Tilemap.from_tilemap(level.tilemap, 0, 0, level.tilemap.width, level.tilemap.height)

        # TODO
        # keep = set()
        # for pair in world.info.get('destructibleTiles', []):
        #     keep.add(pair[0])
        # destructible_tilemap.filter(keep)

        destructible_tilemap.render(surface_destructible, tileset, TileSurface.NORMAL, tileset, level.alternate_tile_palette_y)
        surfaces['destructible'] = surface_destructible

        # Pickups only. Does not include tile pickups.
        surface_entities_pickups = Surface.empty(level.tilemap.width * Tilemap.TILE_SIZE, level.tilemap.height * Tilemap.TILE_SIZE)
        self._paint_entities(level, surface_entities_pickups, 'pickup', False, False, False)
        surfaces['pickups'] = surface_entities_pickups

        # Bonus pickups only.
        surface_entities_pickups_bonus = Surface.empty(level.tilemap.width * Tilemap.TILE_SIZE, level.tilemap.height * Tilemap.TILE_SIZE)
        pickup_tilemap = Tilemap.from_tilemap(level.tilemap, 0, 0, level.tilemap.width, level.tilemap.height)

        # TODO
        # keep = set()
        # for pair in world.info.get('pickupTiles', []):
        #     keep.add(pair[0])
        # pickup_tilemap.filter(keep)

        pickup_tilemap.render(surface_entities_pickups_bonus, tileset, TileSurface.NORMAL, tileset, level.alternate_tile_palette_y)
        self._paint_entities(level, surface_entities_pickups_bonus, 'diamond', False, False, False)
        surfaces['pickups_bonus'] = surface_entities_pickups_bonus

        # Enemy layer.
        surface_entities_enemies = Surface.empty(level.tilemap.width * Tilemap.TILE_SIZE, level.tilemap.height * Tilemap.TILE_SIZE)
        self._paint_entities(level, surface_entities_enemies, 'enemy', False, False, False)
        surfaces['enemies'] = surface_entities_enemies

        # Debug layer with everything + debug info.
        surface_debug = Surface.empty(level.tilemap.width * Tilemap.TILE_SIZE, level.tilemap.height * Tilemap.TILE_SIZE)
        level.tilemap.render(surface_debug, tileset, TileSurface.NORMAL, tileset, level.alternate_tile_palette_y)

        surface_debug_collision = Surface.empty(level.tilemap.width * Tilemap.TILE_SIZE, level.tilemap.height * Tilemap.TILE_SIZE)
        level.tilemap.render(surface_debug_collision, tileset, TileSurface.COLLISION, tileset, level.alternate_tile_palette_y)
        surface_debug.blit_blend(surface_debug_collision, 0, 0, BlendOp.ALPHA50)

        self._paint_entities(level, surface_debug, None, True, False, True)

        surfaces['debug'] = surface_debug

        for key, surface in surfaces.items():
            filename = environment.path_output / Path('levels_rendered/world{:02}-level{:02}-{}.png'.format(level.world_index + 1, level.level_index + 1, key))
            dir_tree = os.path.dirname(filename)
            os.makedirs(dir_tree, exist_ok=True)

            surface.write_to_png(filename, self._compression_level)

    def _paint_entities(self, level: LevelResource, surface: Surface, category: Optional[str], draw_origin=False, translucent=False, draw_index=False):
        if translucent:
            blend_op = BlendOp.ALPHA50
        else:
            blend_op = BlendOp.ALPHA_SIMPLE

        for entity in level.entities:
            if entity.info.gfx is None:
                continue
            if category is not None and entity.info.category != category:
                continue

            sprite_surfaces: SurfaceListResource = cast(SurfaceListResource, self._resources.get(SurfaceListResource.TYPE, entity.info.gfx))
            if sprite_surfaces is None:
                print('Missing texture "{}" for entity "{}".'.format(entity.info.gfx, entity.info.key))
                continue

            if entity.info.gfx_index < 0 or entity.info.gfx_index >= len(sprite_surfaces.surfaces):
                print('Invalid editor texture frame index {} 0for entity template "{}".'.format(entity.info.gfx_index, entity.info.key))
                continue

            origin_x = entity.x
            origin_y = entity.y

            # TODO: get spawnOffset from entity position component
            #  template.offset_* comes from where? Only in turrican 1?
            sprite_x = origin_x
            sprite_y = origin_y
            # if template.offset_x is None:
            #     sprite_x = 0
            # else:
            #     sprite_x = origin_x + template.offset_x
            # if template.offset_y is None:
            #     sprite_y = 0
            # else:
            #     sprite_y = origin_y + template.offset_y

            sprite_surface_list = [
                (sprite_surfaces.surfaces[entity.info.gfx_index], sprite_x, sprite_y)
            ]

            # TODO bug split multi-surface hack
            # if template.hack is not None:
            #     if template.hack == 'flyer_bug_split':
            #         sprite_surface_list = [
            #             (sprite_surface_list[0][0], 0, sprite_surface_list[0][2] - 35),
            #             (sprite_surface_list[0][0], 0, sprite_surface_list[0][2]),
            #             (sprite_surface_list[0][0], 0, sprite_surface_list[0][2] + 35),
            #         ]

            for sprite_surface, x, y in sprite_surface_list:
                surface.blit_blend(sprite_surface, x, y, blend_op)

            if draw_origin:
                surface.box_fill(origin_x, origin_y, self.ORIGIN_SIZE, self.ORIGIN_SIZE, self.COLOR_ORIGIN, BlendOp.ALPHA50)

            if draw_index:
                surface.box_fill(origin_x - 1, origin_y, len(entity.info.name) * 4 + 1, 7, self.COLOR_ORIGIN, BlendOp.ALPHA)
                surface.text(self._font, origin_x, origin_y, entity.info.name, self.COLOR_TEXT)
