try:
    from string import punctuation
    from sys import argv, version_info, exit
    from os.path import splitext
    from os import remove, makedirs
    from time import sleep
    from boardgamegeek import BoardGameGeek
    from boardgamegeek.exceptions import BoardGameGeekError, BoardGameGeekAPIRetryError, BoardGameGeekAPIError, BoardGameGeekTimeoutError
    from PIL import Image

    if (version_info > (3, 0)):
        from urllib.request import urlretrieve

    else:
        from sys import setdefaultencoding
        from urllib2 import urlopen
        from string import maketrans
        from os.path import isdir
        import logging
        logging.basicConfig()

except(ImportError):
    print("\nYou need to install the boardgamegeek and pillow Python modules for this to work. Run 'pip install boardgamegeek pillow' (without quotes) before using this program.\n")
    exit(1)

# Setting encoding to UTF-8 for Python 2 users
if version_info[0] < 3:
    reload(sys)
    setdefaultencoding('utf8')


def get_list_of_games():
    # list to put all game names in from games.txt
    all_games = []

    try:
        # Py3 has this error
        FileNotFoundError
    except (NameError):
        # Py2 doesn't so if FileNotFoundError then make it IOError
        FileNotFoundError = IOError

    try:
        game_file = argv[1]

    except(IndexError):
        print("\nYou need to give the program a text file (.txt) with a list of games in.\n")

        game_file = input("Where is the text file on your computer? You can just drag and drop the file onto this window and press ENTER.\n-------\n").strip()

    try:
        file_format = splitext(game_file)[1]

        if file_format == ".txt":
            with open(game_file, 'r') as fileobject:
                all_games = [line.strip() for line in fileobject if str(line) != "\n"]

        else:
            print("\nYou need to give the program a text file (.txt) with a list of games in.\n")

    except(FileNotFoundError):
        print("\nYou need to use a valid .txt file.\n\nRun 'python main.py' then specify the file or run 'python main.py path/to/valid_text_file.txt'\n")
        exit(1)

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
        print(index + " / " + number_of_games + " - " + game)

        try:
            # This will work when name given exactly matches BGG's name
            game_name = bgg.game(game).name

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

    return all_names_and_links, guessed_games, unfindable_games


def download_images(all_names_and_links):
    games_downloaded_sofar = 0
    number_of_games = str(len(all_names_and_links))

    if len(all_names_and_links) > 0:
        print("\nDownloading all the images...\n")

    games_and_image_paths = {}

    for game_name in all_names_and_links:
        games_downloaded_sofar += 1
        print(str(games_downloaded_sofar) + " / " + number_of_games)

        game_image_link = all_names_and_links[game_name]
        file_name = game_image_link.split('/')[-1]  # eg pic1324609.jpg
        file_format = splitext(file_name)[1]  # eg .jpg

        game_name = game_name.lower()

        # removing punctuation from game name
        if (version_info > (3, 0)):
            remove_punctuation = str.maketrans('', '', punctuation)
            game_name = game_name.translate(remove_punctuation)
        else:
            remove_punctuation = maketrans(punctuation, ' '*len(punctuation))
            game_name = game_name.encode('utf-8').translate(remove_punctuation)

        # replacing spaces with underscore
        game_name = game_name.replace("  ", "_")
        game_name = game_name.replace(" ", "_")

        # appending file format to game name
        game_name_plus_format = game_name + file_format

        # making folder 'game_images'. no error if folder already exists
        if (version_info > (3, 0)):
            makedirs("game_images", exist_ok=True)

        else:
            try:
                makedirs("game_images")
            except OSError:
                if not isdir("game_images"):
                    raise

        # downloading the link to /game_images/name_of_game.jpg
        if (version_info > (3, 0)):
            downloaded_image = urlretrieve(game_image_link, "game_images/" + game_name_plus_format)
            games_and_image_paths.update({game_name: downloaded_image[0]})

        else:
            response = urlopen(game_image_link)
            game_path = "game_images/" + game_name_plus_format
            with open(game_path, 'w') as f:
                f.write(response.read())
                games_and_image_paths.update({game_name: game_path})

    return games_and_image_paths


def resize_images(games_and_image_paths, guessed_games, unfindable_games):

    images_resized_sofar = 0
    number_of_images = str(len(games_and_image_paths))

    if len(games_and_image_paths) > 0:
        print("\nResizing all the images...\n")

    processed_guessed_games = []

    for guessed_game in guessed_games:
        guessed_game = guessed_game.lower()

        # removing punctuation from game name
        if (version_info > (3, 0)):
            remove_punctuation = str.maketrans('', '', punctuation)
            guessed_game = guessed_game.translate(remove_punctuation)
        else:
            remove_punctuation = maketrans(punctuation, ' '*len(punctuation))
            guessed_game = guessed_game.encode('utf-8').translate(remove_punctuation)

        # replacing spaces with underscores
        guessed_game = guessed_game.replace("  ", "_")
        guessed_game = guessed_game.replace(" ", "_")

        processed_guessed_games.append(guessed_game)

    for game in games_and_image_paths:
        images_resized_sofar += 1
        print(str(images_resized_sofar) + " / " + number_of_images)

        image_file = games_and_image_paths[game]
        image = Image.open(image_file)

        longest_dimension = max(image.size)

        # If longest dimension is less than 500px
        # Make a square of largest side
        if longest_dimension < 500:
            size = (longest_dimension, longest_dimension)

        # Otherwise, crop the square to 500px
        else:
            size = (500, 500)

        image.thumbnail(size, Image.ANTIALIAS)
        background = Image.new('RGBA', size, (255, 255, 255, 0))
        background.paste(
            image, (int((size[0] - image.size[0]) / 2),
                    int((size[1] - image.size[1]) / 2))
        )

        if game in processed_guessed_games:
            if (version_info > (3, 0)):
                makedirs("game_images/check_these_images", exist_ok=True)

            else:
                try:
                    makedirs("game_images/check_these_images")
                except OSError:
                    if not isdir("game_images/check_these_images"):
                        raise

            background.save("game_images/check_these_images/" + game + ".png")

        else:
            background.save("game_images/" + game + ".png")

        file_format = splitext(image_file)[1]
        if file_format != ".png":
            remove(image_file)

    if len(games_and_image_paths) > 0:
        print("\n__________\nFinished. Your images should be in a folder called 'game_images' now.\n")

    if len(processed_guessed_games) > 0:
        print("The program had to guess which game you meant for some games. It chose the highest ranked game that loosely matched the name you gave. The images for those games are in a folder called 'game_images/check_these_images' so you can double-check them.\n")

    if len(unfindable_games) > 0:
        unfindable_games = ", ".join(unfindable_games)

        print("__________\nThese games couldn't be found: \n\n" + unfindable_games + "\n\nThe game probably isn't in Board Game Geek's database.\n\nIf you're sure that the games you're requesting are correct and in Board Game Geek's database, try again with just those games in your 'games.txt' file.\n__________")


# Running the program

if __name__ == "__main__":
    all_games = get_list_of_games()
    all_names_and_links, guessed_games, unfindable_games = get_image_links(all_games)
    games_and_image_paths = download_images(all_names_and_links)
    resize_images(games_and_image_paths, guessed_games, unfindable_games)
