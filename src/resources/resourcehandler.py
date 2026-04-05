import json
from pathlib import Path
from typing import Type, List, Dict

from environment import Environment
from loaders.loaderbase import LoaderBase
from processors.processorbase import ProcessorBase
from renderlib.stream_read import StreamRead, Endianness
from resources.resourcelist import ResourceList
from writers.writerbase import WriterBase


class ResourceHandler:

    def __init__(self, environment: Environment):
        self._environment: Environment = environment

        self._loaders: List[LoaderBase] = []
        self._processors: List[ProcessorBase] = []
        self._writers: Dict[List[WriterBase]] = {}

        self._resources: ResourceList = ResourceList()

    def register_loader(self, loader_class: Type[LoaderBase]):
        self._loaders.append(loader_class(self._resources))

    def register_processor(self, processor_class: Type[ProcessorBase]):
        self._processors.append(processor_class())

    def register_writer(self, writer_class: Type[WriterBase]):
        type_list = self._writers.get('type')
        if type_list is None:
            self._writers[writer_class.TYPE] = []

        self._writers[writer_class.TYPE].append(writer_class(self._resources))

    def load_resources(self):
        for loader in self._loaders:
            list_filename = self._environment.path_game / Path('resources/{}.json'.format(loader.TYPE))
            if not list_filename.exists():
                continue

            with open(list_filename, 'r') as f:
                resource_list_data = json.load(f)

            for filename, resource_options_list in resource_list_data.items():
                file_path = self._environment.path_input / Path(filename)
                if not file_path.exists():
                    raise Exception('Resource loader path "{}" does not exist.'.format(file_path))

                stream = StreamRead.from_file(str(file_path), Endianness.BIG)
                for options in resource_options_list:
                    loader.load(stream, options, self._environment)

    def process_resources(self):
        for processor in self._processors:
            processor.process(self._environment, self._resources)

    def write_resources(self):
        for resource in self._resources.resources:
            type_list = self._writers.get(resource.TYPE)
            if type_list is None:
                continue

            for writer in type_list:
                writer.write(resource, self._environment)

    @property
    def resources(self) -> ResourceList:
        return self._resources
