from resources.resourcebase import ResourceBase


class TfmxMusicResource(ResourceBase):

    TYPE = 'music_tfmx'

    def __init__(self, name: str, sample_data: bytes, music_data: bytes):
        super().__init__(name)

        self.sample_data: bytes = sample_data
        self.music_data: bytes = music_data

