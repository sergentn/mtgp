# mtgp - Magic The Gathering Printer

These small scripts allow you to create A4 sheets of MTG proxies in the PNG format, from a decklist in the MTG Arena text format or from any provided image files.

## Install
Tested with Python 3.10.6 on Ubuntu 22.04 as of 2023, April the 1st.

```
python3 -m venv env
source env/bin/activate
python3 -m pip install -r requirements.txt
```

## Usage

- MTG_seeker.py will parse an input decklist written in the MTG Arena format (text file), send requests to the Scryfall API, then create image files in the specified output directory.
- MTG_printer.py will read image files from an input directory (for example, the output directory of MTG_seeker.py) and create ready-to-print A4 sheets in the specified output directory.

Use the provided ExampleDeck.txt to test it:
```
python3 MTG_seeker.py ExampleDeck.txt ExampleCards
python3 MTG_printer.py ExampleCards ExampleSheets
```

Enjoy your home-made high quality proxies :) Nicolas Sergent
