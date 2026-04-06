import json
from pathlib import Path
from typing import cast

from environment import Environment
from renderlib.surface import Surface, BlendOp
from resources.resourcebase import ResourceBase
from resources.surfacelistresource import SurfaceListResource
from writers.writerbase import WriterBase


class SurfaceListWriter(WriterBase):

    TYPE = SurfaceListResource.TYPE

    def write(self, resource: ResourceBase, environment: Environment):
        surface_list: SurfaceListResource = cast(SurfaceListResource, resource)

        # Do not write anything, if nothing needs to be.
        layout = surface_list.get_layout()
        if not len(layout.frames):
            return

        frame_list = []
        target = Surface.empty(layout.size[0], layout.size[1])
        for index, frame in enumerate(layout.frames):
            target.blit(surface_list.surfaces[index], frame.x, frame.y)
            frame_list.append([frame.x, frame.y, frame.width, frame.height])

        # Apply pre-made mask images.
        mask_path = environment.path_game / Path('masks/{}.png'.format(surface_list.name))
        if mask_path.exists():
            mask_surface = Surface.from_png(mask_path)
            target.blit_blend(mask_surface, 0, 0, BlendOp.ALPHA_COPY)

        # Output frame data.
        if len(frame_list) > 1:
            filename_frame_list = environment.path_output / Path('textures/{}.json'.format(surface_list.name))
            filename_frame_list.parent.mkdir(parents=True, exist_ok=True)
            with open(filename_frame_list, 'w') as f:
                f.write(json.dumps(frame_list, indent=2))

        filename_texture = environment.path_output / Path('textures/{}.png'.format(surface_list.name))
        print(filename_texture)
        filename_texture.parent.mkdir(parents=True, exist_ok=True)
        target.write_to_png(filename_texture, 1)
