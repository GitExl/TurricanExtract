from typing import Dict

from environment import Environment
from loaders.loaderbase import LoaderBase
from renderlib.palette import Palette
from renderlib.stream_read import StreamRead
from resources.paletteresource import PaletteResource


class PaletteLoader(LoaderBase):

    TYPE = 'palette'

    def load(self, stream: StreamRead, options: Dict, environment: Environment):
        stream.seek(options.get('offset'))

        name = options.get('name')
        if name is None:
            raise Exception('Palette has no name.')

        length = options.get('length')
        if length is None:
            raise Exception('Palette has no length.')

        bpp = options.get('bpp', 4)
        alpha = options.get('alpha', False)

        palette = Palette.from_stream(stream, length, bpp, alpha)
        self._resources.put(PaletteResource(name, palette))
