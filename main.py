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
    try:
        with open('games.txt', 'r') as fileobject:
            all_games = [line.strip() for line in fileobject if str(line) != "\n"]

    except(FileNotFoundError):
        print("You need to have a file called 'games.txt' in the same folder as this program for this to work.")
        # break
    return all_games


def get_image_links(all_games):
    # dictionary to put all BGG game names and game links in
    all_names_and_links = {}

    # games that absolutely couldn't be found
    unfindable_games = []

    # games that the program guessed the right name for
    guessed_games = []

    # for the progress counter
    number_of_games = str(len(all_games))

    if len(all_games) > 0:
        print("\nGetting the links to the images from Board Game Geek...\n")

    bgg = BoardGameGeek()
    for game in all_games:
        index = str(all_games.index(game) + 1)
        print(index + " / " + number_of_games + " – " + game)

        try:
            # This will work when name given exactly matches BGG's name
            game_name = bgg.game(game).name  # Russian Railroads

        # If there's some other error
        except (BoardGameGeekAPIRetryError, BoardGameGeekAPIError, BoardGameGeekTimeoutError):
            unfindable_games.append(game)
            sleep(5)
            continue

        # If there's a typo or eg, 'Caverna' not 'Caverna: The Cave Farmers'
        except (BoardGameGeekError, AttributeError):
            print('Trying to find the right game...\n')
            # Try to find unfindable games
            # Returns highest ranked game that loosely matches
            # the incorrect game name in games.txt
            # Eg, Ticket to Ride Europe should return Ticket to Ride: Europe
            # but will not return some unofficial expansion pack

            # Get a list of possible BGG ids that the game could be
            potential_games = bgg.search(game)

            # If the search query returns 0 results
            if len(potential_games) < 1:
                unfindable_games.append(game)
                print("Couldn't find {}\n".format(game))
                continue

            # extract just the ids from that list and make new list
            potential_ids = [str(potential_game).split()[-1][:-1] for potential_game in potential_games]

            # get the highest ranked game rank from the ids in potential_ids
            highest_rank = min([bgg.game(game_id=potential_id).ranks[0]['value'] for potential_id in potential_ids if bgg.game(game_id=potential_id).ranks[0]['value'] is not None])

            # get the game name that has the highest rank in that list
            game_name = [bgg.game(game_id=potential_id).name for potential_id in potential_ids if bgg.game(game_id=potential_id).ranks[0]['value'] == highest_rank]

            game_name = game_name[0]
            guessed_games.append(game_name)
            print("Assuming that the game you're looking for is {}...\n".format(game_name))

            sleep(5)
            pass

        # Continues here once game name is established
        game_image_link = bgg.game(game_name).image
        # eg. https://cf.geekdo-images.com/images/pic1772936.jpg

        print("Successfully found {}.\n".format(game_name))

        all_names_and_links.update({game_name: game_image_link})

        # The rate limiting on BGG's API is strict
        # Wait 5 seconds between requests
        sleep(5)

    if len(unfindable_games) > 0:
        unfindable_games = ", ".join(unfindable_games)

        print("__________\nThese games couldn't be found: \n\n" + unfindable_games + "\n\nEither: a) the game isn't in Board Game Geek's database, or b) the request to Board Game Geek timed out.\n\nIf you're sure that the games you're requesting are correct and in Board Game Geek's database, try again with just those games in your 'games.txt' file.\n\n__________")

    return all_names_and_links, guessed_games


def download_images(all_names_and_links):

    if len(all_names_and_links) > 0:
        print("\nDownloading all the images...\n")

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


def resize_images(games_and_image_paths, guessed_games):

    if len(games_and_image_paths) > 0:
        print("\nResizing all the images...\n")

    processed_guessed_games = []

    for guessed_game in guessed_games:
        guessed_game = guessed_game.lower()

        # removing punctuation from game name
        remove_punctuation = str.maketrans('', '', punctuation)
        guessed_game = guessed_game.translate(remove_punctuation)

        # replacing spaces with underscore
        guessed_game = guessed_game.replace(" ", "_")
        processed_guessed_games.append(guessed_game)

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

        if game in processed_guessed_games:
            makedirs("game_images/check_these_images", exist_ok=True)
            background.save("game_images/check_these_images/" + game + ".png")

        else:
            background.save("game_images/" + game + ".png")

        # remove(image_file)

    if len(games_and_image_paths) > 0:
        print("\nFinished. Your images should be in a folder called 'game_images' now.\n")

    if len(processed_guessed_games) > 0:
        print("If the program had to guess which game you meant then the images for that game are in a folder called 'game_images/check_these_images'.\n")


# Running the program

if __name__ == "__main__":
    all_games = get_list_of_games()
    all_names_and_links, guessed_games = get_image_links(all_games)
    games_and_image_paths = download_images(all_names_and_links)
    resize_images(games_and_image_paths, guessed_games)
