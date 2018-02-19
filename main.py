from string import punctuation
from pathlib import Path
from os import remove, makedirs
from time import sleep
from urllib.request import urlretrieve
from gooey import Gooey, GooeyParser
from boardgamegeek import BoardGameGeek
from boardgamegeek.exceptions import BoardGameGeekError, BoardGameGeekAPIRetryError, BoardGameGeekAPIError, BoardGameGeekTimeoutError
from PIL import Image


@Gooey(program_name="BGG Image Downloader", program_description="Finds, downloads, and resizes images from Board Game Geek")
def main():
    parser = GooeyParser()
    parser.add_argument('GameFile',
                        help="Select a text file (.txt) of game names",
                        widget="FileChooser")

    parser.add_argument("OutputDirectory",
                        help="Select the directory to save images in",
                        widget="DirChooser")

    parser.add_argument('-d', '--duration', default=5,
                        type=int, help='Seconds to wait between BGG requests. You can probably make this lower if you only want to download a small number of images.')

    args = parser.parse_args()

    game_file = args.GameFile
    output_directory = Path(args.OutputDirectory)
    sleep_duration = args.duration

    def get_list_of_games():
        with open(game_file, 'r', encoding="UTF-8") as fileobject:
            all_games = [line.strip() for line in fileobject]
        return all_games

    def get_image_links(all_games):
        # dictionary to put all BGG game names and game links in
        all_names_and_links = {}

        # games that absolutely couldn't be found
        unfindable_games = []

        # games that the program guessed the right name for
        guessed_games = []
        bgg = BoardGameGeek()

        for game in all_games:
            try:
                # This will find the game when name given exactly matches BGG's name
                game_name = bgg.game(game).name

            # If there's an error then add to unfindable games
            except (BoardGameGeekAPIRetryError, BoardGameGeekAPIError, BoardGameGeekTimeoutError):
                unfindable_games.append(game)
                sleep(sleep_duration)
                continue

            # If there's a typo or eg, 'Caverna' not 'Caverna: The Cave Farmers'
            except (BoardGameGeekError, AttributeError):
                print('Trying to find the right game...\n')

                # Try to find unfindable games
                # Returns game with the most votes that loosely matches
                # the incorrect game name in games.txt
                # Eg, Ticket to Ride Europe should return Ticket to Ride: Europe
                # but will not return some unofficial expansion pack

                try:
                    # Get a list of possible BGG ids that the game could be
                    potential_games = bgg.search(game)

                except (BoardGameGeekAPIRetryError, BoardGameGeekAPIError, BoardGameGeekTimeoutError, AttributeError):
                    unfindable_games.append(game)
                    sleep(sleep_duration)
                    continue

                # If the search query returns 0 results, then can't find game
                if len(potential_games) < 1:
                    unfindable_games.append(game)
                    print("Couldn't find {}\n".format(game))
                    continue

                # extract just the id numbers from that list and put them in a new list
                potential_ids = [str(potential_game).split()[-1][:-1]
                                 for potential_game in potential_games]

                try:
                    # get number of votes for the game with the most votes from the ids in potential_ids
                    highest_rank = max([bgg.game(game_id=potential_id).users_rated for potential_id in potential_ids if bgg.game(
                        game_id=potential_id).users_rated is not None])
                    sleep(sleep_duration)

                except (BoardGameGeekAPIRetryError, BoardGameGeekAPIError, BoardGameGeekTimeoutError, AttributeError):
                    unfindable_games.append(game)
                    sleep(sleep_duration)
                    continue

                try:
                    # get the game name that has the most votes
                    game_name = [bgg.game(game_id=potential_id).name for potential_id in potential_ids if bgg.game(
                        game_id=potential_id).users_rated == highest_rank]
                    sleep(sleep_duration)

                except (BoardGameGeekAPIRetryError, BoardGameGeekAPIError, BoardGameGeekTimeoutError, AttributeError):
                    unfindable_games.append(game)
                    sleep(sleep_duration)
                    continue

                game_name = game_name[0]

                # Append guessed name to list of guessed names to allow later manual checking
                guessed_games.append(game_name)
                print(
                    "Assuming that the game you're looking for is {}...\n".format(game_name))

                sleep(sleep_duration)
                pass

                # Continues here once game name is established
            try:
                # Get the image link from BGG
                game_image_link = bgg.game(game_name).image
                # eg. https://cf.geekdo-images.com/images/pic1772936.jpg
                sleep(sleep_duration)

            except (BoardGameGeekAPIRetryError, BoardGameGeekAPIError, BoardGameGeekTimeoutError, AttributeError):
                unfindable_games.append(game)
                sleep(sleep_duration)
                continue

            print("Successfully found {}.\n".format(game_name))

            # Once successful, adds game name and image link to a dictionary
            all_names_and_links.update({game_name: game_image_link})

            # The rate limiting on BGG's API is strict
            # Wait 5 seconds between requests
            sleep(sleep_duration)

        # Writes all unfindable games to a text file to allow manual checking
        if len(unfindable_games) > 0:
            with open(output_directory / "unfindable_games.txt", 'a') as f:
                for unfindable_game in unfindable_games:
                    f.write(unfindable_game + "\n")

        return all_names_and_links, guessed_games, unfindable_games

    def download_images(all_names_and_links):

        # Dictionary of game names and the path to the downloaded image
        games_and_image_paths = dict()

        for game_name in all_names_and_links:
            try:
                game_image_link = all_names_and_links[game_name]
                file_format = Path(game_image_link).suffix
                game_name = game_name.lower()

                # removing punctuation from game name
                remove_punctuation = str.maketrans('', '', punctuation)
                game_name = game_name.translate(remove_punctuation)

                # replacing spaces with underscore
                game_name = game_name.replace("  ", "_")
                game_name = game_name.replace(" ", "_")

                # appending file format to game name
                game_name_plus_format = game_name + file_format

                # making folder 'game_images'. no error if folder already exists
                makedirs(output_directory / "game_images", exist_ok=True)

                # downloading the link to /game_images/name_of_game.jpg
                downloaded_image = urlretrieve(
                    game_image_link, output_directory / "game_images" / game_name_plus_format)

                downloaded_image_path = downloaded_image[0]

                games_and_image_paths[game_name] = downloaded_image_path

            except (AttributeError):
                # Writing undownloadable games to a text file
                print(
                    game_name + " couldn't be downloaded for some reason. It'll be saved in 'undownloadable_games.txt'.")
                with open(output_directory / "undownloadable_games.txt", 'a') as f:
                    f.write(game_name + "\n")

        return games_and_image_paths

    def resize_images(games_and_image_paths, guessed_games, unfindable_games):
        """Takes downloaded images, applies transparent padding to make it square, resizes images"""

        if len(games_and_image_paths) > 0:
            print("\nResizing all the images...\n")

        # List to put names of guessed games
        # to sort into separate folder to allow manual checking
        processed_guessed_games = []

        for guessed_game in guessed_games:
            guessed_game = guessed_game.lower()

            # removing punctuation from game name
            remove_punctuation = str.maketrans('', '', punctuation)
            guessed_game = guessed_game.translate(remove_punctuation)

            # replacing spaces with underscores
            guessed_game = guessed_game.replace("  ", "_")
            guessed_game = guessed_game.replace(" ", "_")

            processed_guessed_games.append(guessed_game)

        for game, image_file in games_and_image_paths.items():

            # Opening image file
            # image_file = games_and_image_paths[game]
            image = Image.open(image_file)

            # Determining longest side of file
            longest_dimension = max(image.size)

            # If longest dimension is less than 500px
            # Make a square of largest side
            if longest_dimension < 500:
                size = (longest_dimension, longest_dimension)

            # Otherwise, crop the square to 500px
            else:
                size = (500, 500)

            # Makes a transparent background and pastes game image over the centre
            image.thumbnail(size, Image.ANTIALIAS)
            background = Image.new('RGBA', size, (255, 255, 255, 0))
            background.paste(
                image, (int((size[0] - image.size[0]) / 2),
                        int((size[1] - image.size[1]) / 2))
            )

            game_save_name = game + ".png"
            # Saves new game image in folder
            if game in processed_guessed_games:
                makedirs(output_directory / "game_images" /
                         "check_these_images", exist_ok=True)
                background.save(output_directory / "game_images" /
                                "check_these_images" / game_save_name)

            else:
                background.save(output_directory /
                                "game_images" / game_save_name)

            # Removes original, downloaded image
            # as long as the new image doesn't have the same name
            file_format = Path(image_file).suffix
            if file_format != ".png":
                remove(image_file)

        # Report the program's finished
        if len(games_and_image_paths) > 0:
            print("\n__________\nFinished!\n\nYour images should now be in a folder called 'game_images' within your output directory.\n")

        # Report some games had to be guesses as name given
        # didn't precisely match a BGG game name
        if len(processed_guessed_games) > 0:
            print("The program had to guess which game you meant for some games. It chose the highest ranked game that loosely matched the name you gave. The images for those games are in a folder called 'game_images/check_these_images' so you can double-check them.\n")

        # Report unfindable games and where to find a list of them
        if len(unfindable_games) > 0:
            print("__________\nSome games couldn't be found.\n\nThey're saved in a file called 'unfindable_games.txt' in your output directory.\n\nThe game either isn't in Board Game Geek's database or you just need to rename it to the name in their database.\n\nIf you're sure that the games you're requesting are correct and in Board Game Geek's database, try again with just those games in your 'games.txt' file.\n__________")

    all_games = get_list_of_games()
    all_names_and_links, guessed_games, unfindable_games = get_image_links(
        all_games)
    games_and_image_paths = download_images(all_names_and_links)
    resize_images(games_and_image_paths, guessed_games, unfindable_games)


main()
