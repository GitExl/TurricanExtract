from pathlib import Path

from environment import Environment
from loaders.bitmaploader import BitmapLoader
from loaders.paletteloader import PaletteLoader
from loaders.worldloader import TurricanWorldLoader
from processors.compositesprocessor import CompositesProcessor
from processors.tileentityprocessor import TileEntityProcessor
from resources.resourcehandler import ResourceHandler
from writers.levelimagewriter import LevelImageWriter
from writers.levelwriter import LevelWriter
from writers.palettewriter import PaletteWriter
from writers.surfacelistwriter import SurfaceListWriter
from writers.tilesetwriter import TileSetWriter


def extract():
    game_name = 'turrican1cdtv'

    # TODO: w2l2_boss, all graphics should use color_zero maks, since there are white pixels where holes should be

    environment = Environment(
        Path('game_data/{}'.format(game_name)),
        Path('game_info/{}'.format(game_name)),
        Path('output/{}'.format(game_name))
    )

    resource_handler = ResourceHandler(environment)

    resource_handler.register_loader(PaletteLoader)
    resource_handler.register_loader(BitmapLoader)
    resource_handler.register_loader(TurricanWorldLoader)

    resource_handler.register_processor(CompositesProcessor)
    resource_handler.register_processor(TileEntityProcessor)

    resource_handler.register_writer(LevelWriter)
    resource_handler.register_writer(PaletteWriter)
    resource_handler.register_writer(SurfaceListWriter)
    resource_handler.register_writer(TileSetWriter)
    resource_handler.register_writer(LevelImageWriter)

    resource_handler.load_resources()
    resource_handler.process_resources()
    resource_handler.write_resources()


extract()
