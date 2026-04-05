from pathlib import Path


class Environment:

    def __init__(self, path_game: Path, path_input: Path, path_output: Path):
        self.path_game: Path = path_game
        self.path_input: Path = path_input
        self.path_output: Path = path_output
