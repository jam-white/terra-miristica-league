from players import add_player
from file_manager import get_player_stats
from games import add_game, recalculate_ratings

HEADER = "==============================================\n" \
         "** Welcome to the Terra Mystica League tracker! **\n"

PROMPT = "What would you like to do?\n"\
         "-- Type 'stats' to get a list of players and their stats.\n"\
         "-- Type 'player' to add a new player.\n"\
         "-- Type 'game' to add a new game.\n"\
         "-- Type 'recalculate' to recalculate player stats based on games in the database.\n"


def run():
    # Prompt user for command
    response = input(PROMPT).lower()
    while response not in ["stats", "game", "player", "recalculate"]:
        print("Invalid command.")
        response = input(PROMPT).lower()

    # Run according to response
    if response == "stats":
        print(get_player_stats())
    elif response == "game":
        add_game()
    elif response == "player":
        new_player = input("Which player do you want to add? ")
        add_player(new_player)
    elif response == "recalculate":
        recalculate_ratings()

    # Ask if user wants to do something else
    again = input("Do you want to do something else (Y or N)? ").upper()
    if (again == "Y") or (again == "YES"):
        run()


print(HEADER)
run()
