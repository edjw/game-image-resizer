from string import punctuation
from os.path import splitext
from os import remove, makedirs
from boardgamegeek import BoardGameGeek
from urllib.request import urlretrieve
from PIL import Image


def get_list_of_games():
    # list to put all game names in from games.txt
    all_games = []
    with open('games.txt', 'r') as fileobject:
        all_games = [line.strip() for line in fileobject if str(line) != "\n"]
    return all_games


def get_image_links(all_games):
    # dictionary to put all BGG game names and game links in
    all_names_and_links = {}
    bgg = BoardGameGeek()
    for game in all_games:
        game = bgg.game(game)
        game_name = game.name
        game_image_link = game.image
        all_names_and_links.update({game_name: game_image_link})
    return all_names_and_links


def download_images(all_names_and_links):
    games_and_image_paths = {}

    for game_name in all_names_and_links:
        game_image_link = all_names_and_links[game_name]
        file_name = game_image_link.split('/')[-1]  # eg pic1324609.jpg
        file_format = splitext(file_name)[1]  # eg .jpg

        game_name = game_name.lower()

        # removing punctuation from game name
        remove_punctuation = str.maketrans('', '', punctuation)
        game_name = game_name.translate(remove_punctuation)

        # replacing spaces with underscore
        game_name = game_name.replace(" ", "_")

        # appending file format to game name
        game_name_plus_format = game_name + file_format

        # making folder 'game_images'. no error if folder already exists
        makedirs("game_images", exist_ok=True)

        # downloading the link to /game_images/name_of_game.jpg
        downloaded_image = urlretrieve(
            game_image_link, "game_images/" + game_name_plus_format)
        games_and_image_paths.update({game_name: downloaded_image[0]})
    return games_and_image_paths


def resize_images(games_and_image_paths):
    for game in games_and_image_paths:
        image_file = games_and_image_paths[game]
        size = (500, 500)
        image = Image.open(image_file)
        image.thumbnail(size, Image.ANTIALIAS)
        background = Image.new('RGBA', size, (255, 255, 255, 0))
        background.paste(
            image, (int((size[0] - image.size[0]) / 2),
                    int((size[1] - image.size[1]) / 2))
        )
        background.save("game_images/" + game + ".png")
        remove(image_file)


# running the program

if __name__ == "__main__":
    all_games = get_list_of_games()
    all_names_and_links = get_image_links(all_games)
    games_and_image_paths = download_images(all_names_and_links)
    resize_images(games_and_image_paths)
