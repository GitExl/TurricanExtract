import argparse
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
    parser = argparse.ArgumentParser(
        prog='TurricanExtract',
        description='Extracts levels, tiles, objects, graphics and palettes from the CDTV versions of Turrican 1 and Turrican 2.',
    )
    parser.add_argument('game')
    args = parser.parse_args()

    # TODO: w2l2_boss, all graphics should use color_zero maks, since there are white pixels where holes should be

    environment = Environment(
        Path('game_info/{}'.format(args.game)),
        Path('game_data/{}'.format(args.game)),
        Path('output/{}'.format(args.game))
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

    print('Extracting from {}'.format(args.game))
    resource_handler.load_resources()
    resource_handler.process_resources()

    print('Writing data')
    resource_handler.write_resources()


extract()
