A simple text adventure template using python and json, made to easily create command prompt text adventures.

## Capabilities
+ toggable availability of multiple save slots
+ multi-layered dialogue possible within one section
+ multiple actions possible per section

## Usage
Download the files and adjust the mainmenu and newgame json files as you like. 

For easy section creation, there is also a section template to just copy into newgame and edit. Make sure that the top variable "current_section" of newgame.json is set to the id of the first section of your game.

## Export
I tested exporting with [pyInstaller](https://pypi.org/project/pyinstaller/) and [auto-py-to-exe](https://pypi.org/project/auto-py-to-exe/) but you can use any form of exporting but I am not sure that it will work properly.
