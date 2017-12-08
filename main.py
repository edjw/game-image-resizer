from string import punctuation
from os.path import splitext
from os import remove, makedirs
from time import sleep
from boardgamegeek import BoardGameGeek
from boardgamegeek.exceptions import BoardGameGeekError, BoardGameGeekAPIRetryError, BoardGameGeekAPIError, BoardGameGeekTimeoutError
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
    number_of_games = str(len(all_games))
    unfindable_games = []
    bgg = BoardGameGeek()
    for game in all_games:
        index = str(all_games.index(game) + 1)
        print(index + " / " + number_of_games + " – " + game)

        try:
            game_name = bgg.game(game).name  # Russian Railroads; taken straight from games.txt
            game_image_link = bgg.games(game).image
            # https://cf.geekdo-images.com/images/pic1772936.jpg

            all_names_and_links.update({game_name: game_image_link})

            # The rate limiting on BGG's API is strict
            # Wait 5 seconds between requests
            sleep(5)

        except (BoardGameGeekAPIRetryError, BoardGameGeekAPIError, BoardGameGeekTimeoutError, AttributeError):
            unfindable_games.append(game)
            sleep(5)
            continue

        except (BoardGameGeekError):
            unfindable_games.append(game)
            sleep(5)
            continue


    unfindable_games = ", ".join(unfindable_games)
    print("__________\nThese games couldn't be found: \n\n" + unfindable_games + "\n\nEither: a) the game in your 'games.txt' doesn't precisely match the name of the game in Board Game Geek's database, b) the game isn't in Board Game Geek's database, or c) the request to Board Game Geek timed out.\n\nIf you're sure that the games you're requesting are correct and in Board Game Geek's database, try again with just those games in your 'games.txt' file.\n\nDownloading and processsing the found images now...\n__________\n")

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
    print("\nFinished. Your images should be in a folder called 'game_images' now.\n\n")


# Running the program

if __name__ == "__main__":
    all_games = get_list_of_games()
    all_names_and_links = get_image_links(all_games)
    games_and_image_paths = download_images(all_names_and_links)
    resize_images(games_and_image_paths)
