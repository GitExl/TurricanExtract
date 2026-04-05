import json
from pathlib import Path
from typing import cast

from environment import Environment
from processors.processorbase import ProcessorBase
from renderlib.surface import Surface, BlendOp
from resources.resourcelist import ResourceList
from resources.surfacelistresource import SurfaceListResource


class CompositesProcessor(ProcessorBase):

    def process(self, environment: Environment, resources: ResourceList):
        with open(environment.path_game / Path('composites.json'), 'r') as f:
            composites = json.load(f)

        for composite in composites:
            name = composite.get('name')
            if name is None:
                raise Exception('Composite is missing a name.')

            width, height = composite.get('size')
            if width is None or height is None:
                raise Exception('Composite "{}" has an incorrect size.'.format(name))

            if 'graphics' not in composite:
                raise Exception('Composite "{}" has no graphics.'.format(name))

            surface = Surface.empty(width, height)
            surface.fill(0x00000000)

            for graphic in composite['graphics']:
                if len(graphic) == 4:
                    mod = None
                    source_resource_name, frame_index, x, y = graphic
                elif len(graphic) == 5:
                    source_resource_name, frame_index, x, y, mod = graphic
                else:
                    raise Exception('Composite "{}" has an invalid graphic definition.'.format(name))

                source_surfaces = cast(SurfaceListResource, resources.get(SurfaceListResource.TYPE, source_resource_name))
                if source_surfaces is None:
                    raise Exception('Unable to find surface list "{}" for "{}" composite.'.format(source_resource_name, name))

                source_surface = source_surfaces.surfaces[frame_index]
                if mod == 'flip_y':
                    source_surface = source_surface.flipped_y()

                surface.blit_blend(source_surface, x, y, BlendOp.ALPHA)

            resource = resources.get(SurfaceListResource.TYPE, name)
            if resource is None:
                resource = SurfaceListResource(name)
            resource.add_surface(surface)
            resources.put(resource)
