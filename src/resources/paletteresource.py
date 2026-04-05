from renderlib.palette import Palette
from resources.resourcebase import ResourceBase


class PaletteResource(ResourceBase):

    TYPE = 'palette'

    def __init__(self, name: str, palette: Palette):
        super().__init__(name)

        self.palette: Palette = palette
