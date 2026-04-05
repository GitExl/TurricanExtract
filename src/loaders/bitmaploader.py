from typing import Dict

from environment import Environment
from loaders.loaderbase import LoaderBase
from renderlib.bitplane import BitplaneType, Bitplane, MaskMode
from renderlib.stream_read import StreamRead
from resources.paletteresource import PaletteResource
from resources.surfacelistresource import SurfaceListResource


class BitmapLoader(LoaderBase):

    TYPE = 'bitmap'

    def load(self, stream: StreamRead, options: Dict, environment: Environment):
        if options.get('skip', False):
            return

        if 'name' not in options:
            raise Exception('Bitmap has no name.')
        if 'width' not in options:
            raise Exception('Bitmap has no width.')
        if 'height' not in options:
            raise Exception('Bitmap has no height.')
        if 'planes' not in options:
            raise Exception('Bitmap has no planes.')
        if 'count' not in options:
            raise Exception('Bitmap has no count.')
        if 'offset' not in options:
            raise Exception('Bitmap has no offset.')
        if 'palette' not in options:
            raise Exception('Bitmap has no palette.')
        if 'mode' not in options:
            raise Exception('Bitmap has no mode.')

        name = options['name']
        width = options['width']
        height = options['height']
        planes = options['planes']
        count = options['count']
        offset = options['offset']
        palette_key = options['palette']
        mode_key = options['mode']
        masking = options.get('mask', 'none')
        flip_y = options.get('flip_y', False)
        export = options.get('export', True)

        palette_resource = self._resources.get(PaletteResource.TYPE, palette_key)
        if palette_resource is None:
            raise Exception('Bitmap references unknown palette "{}".'.format(palette_key))
        palette = palette_resource.palette

        if mode_key == 'amiga_sprite':
            mode = BitplaneType.AMIGA_SPRITE
        elif mode_key == 'chunky':
            mode = BitplaneType.CHUNKY
        elif mode_key == 'planar':
            mode = BitplaneType.PLANAR
        else:
            raise Exception('Bitmap uses unknown bitplane mode "{}".'.format(mode_key))

        surface_list = self._resources.get(SurfaceListResource.TYPE, name)
        if surface_list is None:
            surface_list = SurfaceListResource(name)
            self._resources.put(surface_list)

        stream.seek(offset)
        for _ in range(0, count):
            bitmap = Bitplane.from_stream(stream, mode, width, height, planes)

            mask_color = 0
            mask = None
            mask_mode = MaskMode.NONE
            for masking_key in masking.split(','):
                masking_key = masking_key.strip()

                if masking_key == 'none':
                    continue
                elif masking_key == 'color_zero':
                    mask_color = 0
                    mask_mode |= MaskMode.INDEX
                elif masking_key[:6] == 'color:':
                    mask_color = int(masking_key[6:])
                    mask_mode |= MaskMode.INDEX
                elif masking_key == 'bitplane':
                    mask_mode |= MaskMode.BITPLANE
                    if mode == BitplaneType.PLANAR:
                        mask = bitmap.from_stream(stream, BitplaneType.PLANAR, width, height, planes)
                    else:
                        mask = bitmap.from_stream(stream, BitplaneType.CHUNKY, width, height, 1)
                else:
                    raise Exception('Unknown mask type "{}".'.format(masking_key))

            surface = bitmap.create_surface(mask, palette, mask_color, 0, mask_mode)
            if flip_y:
                surface = surface.flipped_y()

            surface_list.add_surface(surface, export)
