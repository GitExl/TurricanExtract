# Turrican Extrator

Extracts levels, tiles, objects, graphics and palettes from the CDTV versions of Turrican 1 and
Turrican 2.

## Usage

1. Place Turrican CDTV data into `game_data/turrican1cdtv` or `game_data/turrican2cdtv`. 
2. [Install uv](https://docs.astral.sh/uv/getting-started/installation/).
3. From a commandline window, run `uv run ./src/main.py turrican1cdtv` to extract data from it into `output/turrican1cdtv`.

## Compilation

1. [Install Visual Studio Community](https://visualstudio.microsoft.com/vs/community/).
2. Open `renderlib/renderlib.sln` and compile it.
3. Make sure that `libpng16.dll` and the built `renderlib.dll` file are available when running the main program.