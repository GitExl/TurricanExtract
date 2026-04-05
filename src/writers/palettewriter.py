from pathlib import Path
from typing import cast

from environment import Environment
from renderlib.surface import Surface, BlendOp
from resources.paletteresource import PaletteResource
from resources.resourcebase import ResourceBase
from writers.writerbase import WriterBase


class PaletteWriter(WriterBase):

    TYPE = PaletteResource.TYPE

    def write(self, resource: ResourceBase, environment: Environment):
        palette: PaletteResource = cast(PaletteResource, resource)

        surface = Surface.empty(32, 32)

        x = 0
        y = 0
        for i in range(0, 16):
            surface.box_fill(x, y, 8, 8, palette.palette.get_color(i) | 0xFF000000, BlendOp.SOLID)
            x += 8
            if x >= 32:
                x = 0
                y += 8

        filename = environment.path_output / Path('palettes/{}.png'.format(palette.name))
        filename.parent.mkdir(parents=True, exist_ok=True)
        surface.write_to_png(filename, 1)
