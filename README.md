# Board game image resizer

## Use case

Say you ran a board game shop that had a online shop...

Say you needed to populate your online shop with thousands of square images of the board games you had for sale...

Say you wanted to avoid manually searching for, downloading, renaming and resizing those images...

## What this does

Game image resizer finds and downloads the best image for a list of board games from BoardGameGeek using its API. Then it makes the images square with transparent padding around rectangular images. Then it saves them with a useful, upload-ready filename.

Board Game Geek's API rate limiting is strict so this makes a request every 5 seconds. This means it's slow.

If you make heavy use of BoardGameGeek's API, images and image hosting using this script or otherwise, it would be nice to [donate to them](https://boardgamegeek.com/support).

## How to use this

`pip3 install boardgamegeek, pillow`

or

`pipenv install boardgamegeek, pillow`

Make a text file called `games.txt` with a game's name on each line. *The names in the file must exactly match the game's name on Board Game Geek.*

Save the file in the same folder as `main.py`

Run `python main.py`

It will save the processed images in a folder called `game_images` in the same folder as `main.py`

## To Do

* make it easy for others to use: packaged up for mac/windows/etc with file picker instead of forcing use of games.txt
* some sort of fuzzy matching of game names so games in games.txt don't have to precisely match BGG's name