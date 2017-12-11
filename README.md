# Board game image resizer

## Use case

Say you ran a board game shop that had a online shop...

Say you needed to populate your online shop with thousands of square images of the board games you had for sale...

Say you wanted to avoid manually searching for, downloading, renaming and resizing those images...

## What this does

Game image resizer finds and downloads the best image for a list of board games from BoardGameGeek using its API. Then it makes the images square with transparent padding around rectangular images. Then it saves them with a useful, upload-ready filename.

An image of 200px by 700px will turn out as 500px by 500px. And image of 200px by 400px will turn out as 400px by 400px. Transparent padding is added to retain the original aspect ratio.

Board Game Geek's API rate limiting is strict so this makes a request every 5 seconds. This means it's *slow*.

If you make heavy use of BoardGameGeek's API, images and image hosting using this script or otherwise, it would be nice to [donate to them](https://boardgamegeek.com/support).

## How to use this

This should run on Python 3 and Python 2.

`pipenv install boardgamegeek pillow`

or

`pip install boardgamegeek pillow`

Make a text file called something like `games.txt` with a game's name on each line. It can be stored anywhere.

Run `python main.py path/to/games.txt`

It will save the processed images in a folder called `game_images` in the same folder as `main.py`

Games that only loosely match a game on Board Game Geek will be saved in a subfolder of `game_images` called `game_images/check_these_games` for later checking.

## To Do

* make it easy for others to use: packaged up for mac/windows/etc with a GUI and file picker instead of forcing use of text file