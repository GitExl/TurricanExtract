from math import floor, ceil
from typing import List, Optional, Tuple

from renderlib.surface import Surface
from resources.resourcebase import ResourceBase


class LayoutFrame:

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Layout:

    def __init__(self, surfaces: List[Surface], write: List[bool], target_width: int = 320):
        self._frames: List[LayoutFrame] = []

        self._width: int = 0
        self._height: int = 0

        self._frame_max_width: int = 0
        self._frame_max_height: int = 0

        self._columns: int = 0
        self._rows: int = 0

        self._calculate(surfaces, write, target_width)

    def _calculate(self, surfaces: List[Surface], write: List[bool], target_width: int):
        for surface in surfaces:
            self._frame_max_width = max(self._frame_max_width, surface.width)
            self._frame_max_height = max(self._frame_max_height, surface.height)

        if target_width < self._frame_max_width:
            target_width = self._frame_max_width

        self._columns = int(floor(target_width / self._frame_max_width))
        self._rows = int(ceil(len(surfaces) / self._columns))

        if self._rows == 1:
            self._width = len(surfaces) * self._frame_max_width
        else:
            self._width = self._columns * self._frame_max_width
        self._height = self._rows * self._frame_max_height

        x = 0
        y = 0
        for index, surface in enumerate(surfaces):
            if not write[index]:
                continue

            self._frames.append(LayoutFrame(x, y, surface.width, surface.height))

            x += self._frame_max_width
            if x >= self._width:
                x = 0
                y += self._frame_max_height

    @property
    def frames(self) -> List[LayoutFrame]:
        return self._frames

    @property
    def size(self) -> Tuple[int, int]:
        return self._width, self._height

    @property
    def frame_max_size(self) -> Tuple[int, int]:
        return self._frame_max_width, self._frame_max_height

    @property
    def columns(self) -> int:
        return self._columns

    @property
    def rows(self) -> int:
        return self._rows


class SurfaceListResource(ResourceBase):

    TYPE = 'surface_list'

    def __init__(self, name: str, max_layout_width: int = 320):
        super().__init__(name)

        self.surfaces: List[Surface] = []
        self.write: List[bool] = []
        self.layout: Optional[Layout] = None

        self._max_layout_width: int = max_layout_width

    def get_layout(self) -> Layout:
        if self.layout is None:
            self.layout = Layout(self.surfaces, self.write, self._max_layout_width)

        return self.layout

    def add_surface(self, surface: Surface, write=True):
        self.layout = None
        self.surfaces.append(surface)
        self.write.append(write)
