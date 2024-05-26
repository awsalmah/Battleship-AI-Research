import random
import numpy as np

class BattleshipGame:

    def __init__(self):
        # The icons/keys used to represent board display
        self.chars = {'unknown': '■',
                      'hit': 'X',
                      'miss': '□',
                      'sea': '■',
                      'ship': 'O'}
        self.board1ships = [[self.chars['sea'] for _ in range(10)] for _ in range(10)]
        self.board2ships = [[self.chars['sea'] for _ in range(10)] for _ in range(10)]
        self.board1enemy = [[self.chars['unknown'] for _ in range(10)] for _ in range(10)]
        self.board2enemy = [[self.chars['unknown'] for _ in range(10)] for _ in range(10)]
        self.ships = {'Aircraft Carrier': 5, 'Battleship': 4, 'Submarine': 3, 'Destroyer': 3, 'Patrol Boat': 2}

        # stores the shots made to make sure we don't make the same ones again
        self.shots_made_p1 = set()
        self.shots_made_p2 = set()
        
        # stores the coordinates of the n,s,w,e locations of the targets hit to make sure we hit them
        self.hunting_sim_p1 = set()
        self.hunting_sim_p2= set()

        # this will store the info about the ships, so that we can tell if it has been
        # sunk or not
        self.ship_info_p1 = {ship: {'size': size, 'coordinates': [], 'sunk': False} for ship, size in
                             self.ships.items()}
        self.ship_info_p2 = {ship: {'size': size, 'coordinates': [], 'sunk': False} for ship, size in
                             self.ships.items()}


    # copy board is for Monte Carlo, as we must copy the board and place items on it for simulation.
    # does it work? who knows.
    def copy_board(self, board):
        copied_board = []
        for row in board:
            new_row = []
            for col in row:
                new_row.append(col)
            copied_board.append(new_row)
        return copied_board


    # first implementation of monte carlo.
    # does it work? yes. will it work well? im not sure
    # i think main issue rn comparing our implementation with others is that we dont take into account the fact that
    # a ship may be sunken already while we are adding more probabibility to it.
    # we probably could take that into account but im not sure how we would go about that, plus im tired.
    # so im done for today xoxo - gossip girl (aka jeremy)
    def monte_carlo_simulation(self, board, player):
        num_sims = 1000
        hit_probabilities = np.zeros((10, 10))  # initialize array of 0s.

        coords = []

        lol = 0

        while lol != 10:
            if lol % 2 == 0:
                x = 0
                for i in range(5):
                    coords.append((lol, x))
                    x = x + 2
            else:
                x = 1
                for i in range(5):
                    coords.append((lol, x))
                    x = x + 2
            lol += 1

        for huh in range(0, num_sims):
            simulation_board = self.copy_board(board)
            self.randomly_place_nonsunk_ship(simulation_board, player)

            # calc the probabibility FOR EACH spot on the board
            for row in range(0, 10):
                for col in range(0, 10):

                    if (row, col) in coords:
                        hit_probabilities[row][col] += 3

                    if simulation_board[row][col] == self.chars['sea']:
                        hit_probabilities[row][col] += 7

                        overlap_weight = self.calculate_overlap_weight(simulation_board, row, col)
                        hit_probabilities[row][col] += overlap_weight
                    # if the spot has a ship on it, then we should increase its probabibility.
                    elif simulation_board[row][col] == self.chars['ship']:
                        hit_probabilities[row][col] += 25
                        # overlap_weight = self.calculate_overlap_weight(simulation_board, row, col)
                        # hit_probabilities[row][col] += overlap_weight

        # make them into actual probabibilities by dividing over total
        hit_probabilities = hit_probabilities / num_sims
        # print(hit_probabilities)

        # magic? nah so like what it does is it flattens the array and then finds the max of it
        # then it gets converted back to a tuple which "should" have the highest probability
        max_position = np.unravel_index(np.argmax(hit_probabilities), hit_probabilities.shape)
        return max_position


    def calculate_overlap_weight(self, board, row, col):
        weight = 5
        for d_r, d_c in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            r = row + d_r
            c = col + d_c
            if 0 <= r < 10 and 0 <= c < 10:
                if board[r][c] == self.chars['hit']:
                    weight += 5
        return weight


    #function to print the battleship board
    def print_board(self, board):
        print("\n   A B C D E F G H I J")
        for i in range(10):
            print(i, end='  ')
            for j in range(10):
                print(board[i][j], end=' ')
            print()


    #function to update the ship info
    def update_ship_info(self, player, ship, coords):
        if player == 1:
            self.ship_info_p1[ship]['coordinates'] = coords
        else:
            self.ship_info_p2[ship]['coordinates'] = coords


    #function that checks if a ship has been sunk and displays that a specific ship has been sunk
    def check_sunk(self, player, row, col):
        if player == 1:
            ship_info = self.ship_info_p2
            board = self.board2ships
        else:
            ship_info = self.ship_info_p1
            board = self.board1ships

        for ship, info in ship_info.items():
            if (row, col) in info['coordinates']:
                info['coordinates'].remove((row,col))
                if len(info['coordinates']) == 0:
                    info['sunk'] = True
                    print(f"Player {player} sunk {ship}!")
                    break


    def randomly_place_nonsunk_ship(self, board, player):
        nonsunk_ships = [ship for ship, info in self.ship_info_p1.items() if not info['sunk']] if player == 1 else [
            ship for ship, info in self.ship_info_p2.items() if not info['sunk']]

        x = len(nonsunk_ships)
        for i in range(x):
            selected_ship = nonsunk_ships[i]
            while True:
                row = random.randint(0, 9)
                col = random.randint(0, 9)
                orientation = random.choice(['H', 'V'])
                if self.is_valid_position(board, row, col, orientation, selected_ship):
                    ship_coordinates = self.place_ship(board, selected_ship, row, col, orientation)
                    break


    def place_ship(self, board, ship, row, col, orientation):
        ship_size = self.ships[ship]
        ship_coords=[]

        if orientation == 'H':
            for i in range(self.ships[ship]):
                board[row][col + i] = self.chars['ship']
                ship_coords.append((row, col + i))
        elif orientation == 'V':
            for i in range(self.ships[ship]):
                board[row + i][col] = self.chars['ship']
                ship_coords.append((row + i, col))
        return ship_coords


    def is_valid_position(self, board, row, col, orientation, ship):
        if orientation == 'H' and col + self.ships[ship] > 10:
            return False
        if orientation == 'V' and row + self.ships[ship] > 10:
            return False

        for i in range(self.ships[ship]):
            if orientation == 'H' and board[row][col + i] != self.chars['sea'] and board[row][col + i] != self.chars[
                'miss']: # added final condition for monte carlo. remove if no work anymore.
                return False
            elif orientation == 'V' and board[row + i][col] != self.chars['sea'] and board[row + i][col] != self.chars[
                'miss']: # added final condition for monte carlo. don't know if it works, will fix if it doesn't
                return False
        return True


    def randomly_place_ships(self, board, player):
        for ship in self.ships:
            while True:
                try:
                    row = random.randint(0, 9)
                    col = random.randint(0, 9)
                    orientation = random.choice(['H', 'V'])
                    if self.is_valid_position(board, row, col, orientation, ship):
                        ship_cords = self.place_ship(board, ship, row, col, orientation)
                        self.update_ship_info(player, ship, ship_cords)
                        break
                except ValueError:
                    continue


    def place_ships_near_corners(self, board, player):
        corners = [(0, 0), (0, 9), (9, 0), (9, 9), (1, 1)]
        random.shuffle(corners)

        for i, ship in enumerate(self.ships):
            corner = corners[i]
            orientation = random.choice(['H', 'V'])

            ship_size = self.ships[ship]
            # print(corner)
            if corner == (0, 0):
                ship_coords = self.place_ship(board, ship, 0, 0, orientation)
                self.update_ship_info(player, ship, ship_coords)
                # print(ship)
            elif corner == (1, 1):
                ship_coords = self.place_ship(board, ship, 1, 1, orientation)
                self.update_ship_info(player, ship, ship_coords)
            elif corner == (0, 9):
                if orientation == 'H':
                    ship_coords = self.place_ship(board, ship, 0, 9 - ship_size + 1, orientation)
                    self.update_ship_info(player, ship, ship_coords)
                else:
                    ship_coords = self.place_ship(board, ship, 0, 9, orientation)
                    self.update_ship_info(player, ship, ship_coords)
            elif corner == (9, 0):
                if orientation == 'V':
                    ship_coords = self.place_ship(board, ship, 9 - ship_size + 1, 0, orientation)
                    self.update_ship_info(player, ship, ship_coords)
                else:
                    ship_coords = self.place_ship(board, ship, 9, 0, orientation)
                    self.update_ship_info(player, ship, ship_coords)
            elif corner == (9, 9):
                if orientation == 'V':
                    ship_coords = self.place_ship(board, ship, 9 - ship_size + 1, 9, orientation)
                    self.update_ship_info(player, ship, ship_coords)
                else:
                    ship_coords = self.place_ship(board, ship, 9, 9 - ship_size + 1, orientation)
                    self.update_ship_info(player, ship, ship_coords)


    def place_ships_in_cluster(self, board, player):
        start_row = random.randint(3, 4)
        start_col = random.randint(2, 4)

        ships_to_place = list(self.ships.keys())
        random.shuffle(ships_to_place)

        first = ships_to_place.pop()

        ship_coords = self.place_ship(board, first, start_row, start_col, 'H')
        self.update_ship_info(player, first, ship_coords)

        second = ships_to_place.pop()

        ship_coords = self.place_ship(board, second, start_row + 1, start_col, 'H')
        self.update_ship_info(player, second, ship_coords)

        third = ships_to_place.pop()

        ship_coords = self.place_ship(board, third, start_row - 1, start_col - 1, 'V')
        self.update_ship_info(player, third, ship_coords)

        fourth = ships_to_place.pop()

        ship_coords = self.place_ship(board, fourth, start_row - 2, start_col - 2, 'V')
        self.update_ship_info(player, fourth, ship_coords)

        fifth = ships_to_place.pop()

        ship_coords = self.place_ship(board, fifth, start_row + 2, start_col + 1, 'H')
        self.update_ship_info(player, fifth, ship_coords)

        # print(self.ship_info_p1)


    def hunting_sim(self, player):
        #initialize the variables
        if player == 1: 
            shots_made = self.shots_made_p1 
            shots_to_make = self.hunting_sim_p1
            boardship=self.board2ships
        else: 
            shots_made = self.shots_made_p2
            shots_to_make = self.hunting_sim_p2
            boardship = self.board1ships

        while True:
            #if shots to make is empty, then randomly choose a target 
            if len(shots_to_make) == 0:
                row = random.randint(0, 9)
                col = random.randint(0, 9)
            #if shots to make is not empty then pick a target according to the indices in it
            elif len(shots_to_make) > 0:
                firstelementindex=0
                for index in shots_to_make:
                    if firstelementindex == 0:
                        row = index[0]
                        col = index[1]
                        break
                shots_to_make.discard((row,col))
                
            #if you get a hit, then add the N S E W to the shots to make set if possible so that you are more likely to get another hit
            if (row, col) not in shots_made:
                if boardship[row][col] == self.chars['ship']: 
                    if row+1 <=9 and row+1 >=0 and (row+1, col) not in shots_made: shots_to_make.add((row+1,col))
                    if row-1 >=0 and row-1 <= 9 and (row-1, col) not in shots_made: shots_to_make.add((row-1,col))
                    if col+1 <= ord('J') - 65 and col+1 >= ord('A') - 65 and (row, col+1) not in shots_made: shots_to_make.add((row,col+1))
                    if col-1 >= ord('A') - 65 and col-1 <= ord('J') - 65 and (row, col-1) not in shots_made: shots_to_make.add((row,col-1))
                shots_made.add((row, col))
                return row, col

            
    def random_shot(self, player):
        if player == 1:
            shots_made = self.shots_made_p1
        else:
            shots_made = self.shots_made_p2

        while True:
            row = random.randint(0, 9)
            col = random.randint(0, 9)
            if (row, col) not in shots_made:
                shots_made.add((row, col))
                return row, col


    def take_input(self, player):
        if player == 1:
            shots_made = self.shots_made_p1
        else:
            shots_made = self.shots_made_p2
        while True:
            try:
                row = int(input("Enter row to attack: "))
                col = input("Enter column to attack: ").upper()
                col = ord(col) - 65
                if row < 0 or row > 9 or col < 0 or col > 9:
                    raise ValueError("Invalid position! Row and column must be between 0 and 9.")
                if (row, col) in shots_made:
                    raise ValueError("Invalid position! This position has already been shot.")
                shots_made.add((row, col))
                return row, col
            except ValueError as e:
                print(e)


    def manually_place_ship(self, board, player):
        print(f"\nPlayer {player}, manually place your ships:")
        self.print_board(board)
        for ship in self.ships:
            while True:
                try:
                    print(f"\nPlacing {ship}")
                    row = int(input(f"Enter row for {ship} ({self.ships[ship]}): "))
                    col = input(f"Enter column for {ship} ({self.ships[ship]}): ").upper()
                    col = ord(col) - 65
                    orientation = input("Enter orientation (H for horizontal, V for vertical): ").upper()
                    if orientation not in ['H', 'V']:
                        raise ValueError("Invalid orientation! Please enter H or V.")
                    if row < 0 or row > 9 or col < 0 or col > 9:
                        raise ValueError("Invalid position! Row and column must be between 0 and 9.")
                    if not self.is_valid_position(board, row, col, orientation, ship):
                        raise ValueError("Invalid position! Ship overlaps with another ship.")
                    ship_cords = self.place_ship(board, ship, row, col, orientation)
                    self.update_ship_info(player, ship, ship_cords)
                    self.print_board(board)
                    break
                except ValueError as e:
                    print(e)


    def play(self):
        
        # prompt the user to choose whichever game mode they want 
        while True:
            print("Please choose one of the following modes:")
            print("1. Player vs Player")
            print("2. Player vs AI")
            print("3. AI vs AI")
            player_choice=int(input())
            if player_choice in [1,2,3]: break
            else: print("Please choose one of the given choices\n\n")
        
        if player_choice == 3:
        #choose the kind of ai for player1
            while True:
                print("\nPlease choose the kind of AI that you want player 1 to have:")
                print("1. Random AI")
                print("2. Hunting Strategy AI")
                print("3. Monte Carlo AI")
                player1_AI=int(input())
                if player1_AI in [1,2,3]: break
                else: print("Please choose one of the given choices\n\n")
            #choose the kind of placement for player1
            while True:
                print("\nPlease choose the ship placement strategy that you want player 1 to have:")
                print("1. Random")
                print("2. Cluster")
                print("3. Corner")
                p1placement=int(input())
                if p1placement in [1,2,3]: break
                else: print("Please choose one of the given choices\n\n")
            
        #choose the kind of ai for player2
        if player_choice in [2,3]:
            while True:
                print("\nPlease choose the kind of AI that you want player 2 to have:")
                print("1. Random AI")
                print("2. Hunting Strategy AI")
                print("3. Monte Carlo AI")
                player2_AI=int(input())
                if player2_AI in [1,2,3]: break
                else: print("Please choose one of the given choices\n\n")
            
        #choose the kind of placement for player2
        if player_choice == 3:
            while True:
                print("\nPlease choose the ship placement strategy that you want player 2 to have:")
                print("1. Random")
                print("2. Cluster")
                print("3. Corner")
                p2placement=int(input())
                if p2placement in [1,2,3]: break
                else: print("Please choose one of the given choices\n\n")


        # player 1:
        if player_choice in [1,2]: self.manually_place_ship(self.board1ships, 1)
        elif player_choice == 3:
            if p1placement == 1: self.randomly_place_ships(self.board1ships, 1)
            elif p1placement == 2: self.place_ships_in_cluster(self.board1ships, 1)
            elif p1placement == 3: self.place_ships_near_corners(self.board1ships,1)

        # player 2:
        if player_choice == 1: self.manually_place_ship(self.board2ships, 2)
        elif player_choice == 2: self.randomly_place_ships(self.board2ships, 2)
        elif player_choice == 3: 
            if p2placement == 1: self.randomly_place_ships(self.board2ships, 2)
            elif p2placement == 2: self.place_ships_in_cluster(self.board2ships, 2)
            elif p2placement == 3: self.place_ships_near_corners(self.board2ships,2)
        
        print("Let's start the game!")
        while True:
            print("\nPlayer 1's turn:")
            self.print_board(self.board1enemy)

            #choose whether player 1 is going to be a user or an ai
            if player_choice in [1,2]: row, col = self.take_input(1)
            elif player_choice == 3:
                if player1_AI == 1: row, col = self.random_shot(1)
                if player1_AI == 2: row, col = self.hunting_sim(1)
                elif player1_AI == 3: row, col = self.monte_carlo_simulation(self.board1enemy, 1)

            if self.board2ships[row][col] == self.chars['hit'] or \
                    self.board1enemy[row][col] == self.chars['miss']:
                print("You've already attacked this position!")
                continue
            if self.board2ships[row][col] == self.chars['ship']:
                print("Player 1 hit Player 2's ship!")
                self.board1enemy[row][col] = self.chars['hit']
                self.check_sunk(1, row, col)
                self.board2ships[row][col] = self.chars['hit']

            else:
                print("Player 1 missed!")
                self.board1enemy[row][col] = self.chars['miss']

            self.print_board(self.board1enemy)
            if all(all(cell != self.chars['ship'] for cell in row) for row in self.board2ships):
                print("Player 1 wins!")
                break

            print("\nPlayer 2's turn:")
            self.print_board(self.board2enemy)

            #choose whether player 2 is going to be a user or an ai
            if player_choice == 1: row, col = self.take_input(2)
            elif player_choice in [2,3]:
                if player2_AI == 1: row, col = self.random_shot(2)
                elif player2_AI == 2: row, col = self.hunting_sim(2)
                elif player2_AI == 3: row, col = self.monte_carlo_simulation(self.board2enemy, 2)


            if self.board1ships[row][col] == self.chars['hit'] or \
                    self.board2enemy[row][col] == self.chars['miss']:
                print("You've already attacked this position!")
                continue
            if self.board1ships[row][col] == self.chars['ship']:
                print("Player 2 hit Player 1's ship!")
                self.board2enemy[row][col] = self.chars['hit']
                self.check_sunk(2, row, col)
                self.board1ships[row][col] = self.chars['hit']
            else:
                print("Player 2 missed!")
                self.board2enemy[row][col] = self.chars['miss']

            self.print_board(self.board2enemy)
            if all(all(cell != self.chars['ship'] for cell in row) for row in self.board1ships):
                print("Player 2 wins!")
                break


def main():
    game = BattleshipGame()
    game.play()


if __name__ == "__main__":
    main()
