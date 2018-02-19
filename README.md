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

Standalone builds of this are in the [dist folder](https://github.com/edjw/game-image-resizer/tree/master/dist)

If you run it as as a standalone program on Mac, the image folders are added into your Home directory.

If you run it as as a standalone program on Windows, the image folders are added into the same folder as the program.

Alternatively run it as a script...

`pipenv install boardgamegeek pillow`

or

`pip --user install boardgamegeek pillow`

Make a text file called something like `games.txt` with a game's name on each line. It can be stored anywhere.

Run `python main.py path/to/games.txt`

If you're running this as a script, it will save the processed images in a folder called `game_images` in the same folder as `main.py`

If you're running this as a standalone program, it'll put `game_images` in your home directory.

Games that only loosely match a game on Board Game Geek will be saved in a subfolder of `game_images` called `game_images/check_these_games` for later checking.

## How to build the standalone program

`pip install pyinstaller`

To make a single executable file that packages up everything in the app run:

`pyinstaller main.py -F -n NAME_OF_APP -p VIRTUAL_ENV_FOLDER`

-F makes it a single app. -n specifies the name. -p specifies other folders it should pull in resources from

then

`pyinstaller NAME_OF_APP.spec`

For example:

On Windows

`pyinstaller main.py -F -n bgg_image_resizer_windows -p C:\Users\USERNAME\.virtualenvs\game-image-resizer-cIXL_u_t`

`pyinstaller bgg_image_resizer_windows.spec`

On Mac

`pyinstaller main.py -F -n bgg_image_resizer_mac -p /Users/USERNAME/.local/share/virtualenvs/game-image-resizer-VllgVcYq`

`pyinstaller bgg_image_resizer_mac.spec`
