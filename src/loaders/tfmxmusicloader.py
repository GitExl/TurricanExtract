from typing import Dict

from environment import Environment
from loaders.loaderbase import LoaderBase
from renderlib.stream_read import StreamRead
from resources.tfmxmusicresource import TfmxMusicResource


class TfmxMusicLoader(LoaderBase):

    TYPE = 'music_tfmx'

    def load(self, stream: StreamRead, options: Dict, environment: Environment):
        name = options.get('name')
        if name is None:
            raise Exception('TFMX music has no name.')

        sample_offset = options.get('sampleOffset')
        sample_size = options.get('sampleSize')
        if sample_offset is None or sample_size is None:
            raise Exception('TFMX music is missing sample offset or size.')

        data_offset = options.get('dataOffset')
        data_size = options.get('dataSize')
        if data_offset is None or data_size is None:
            raise Exception('TFMX music is missing data offset or size.')

        stream.seek(sample_offset)
        sample_data = stream.read_bytes(sample_size)

        stream.seek(data_offset)
        music_data = stream.read_bytes(data_size)

        self._resources.put(TfmxMusicResource(name, sample_data, music_data))
