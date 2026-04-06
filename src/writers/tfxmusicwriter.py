from pathlib import Path

from environment import Environment
from resources.resourcebase import ResourceBase
from resources.tfmxmusicresource import TfmxMusicResource
from writers.writerbase import WriterBase


class TfmxMusicWriter(WriterBase):

    TYPE = TfmxMusicResource.TYPE

    def write(self, resource: ResourceBase, environment: Environment):
        music: TfmxMusicResource = resource

        filename_sample_data = environment.path_output / Path('music/smpl.{}'.format(music.name))
        filename_sample_data.parent.mkdir(parents=True, exist_ok=True)
        with open(filename_sample_data, 'wb') as f:
            f.write(music.sample_data)

        filename_music_data = environment.path_output / Path('music/mdat.{}'.format(music.name))
        filename_music_data.parent.mkdir(parents=True, exist_ok=True)
        with open(filename_music_data, 'wb') as f:
            f.write(music.music_data)
