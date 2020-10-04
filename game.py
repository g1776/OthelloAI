import tkinter as tk
import tkinter.font as tkFont
from PIL import ImageTk, Image 
from contextlib import suppress
from functools import partial
import re
import math
from ai import AIOthello
import random

#=================== SETTINGS =====================#

STARTING_PLAYER = 'black'
NUM_PLAYERS = 1
LOG_TURNS = False # toggle general logging
SHOW_GUI = True

DEBUG = False
DEBUG_SETTINGS= {

    # what to show on squares
    # values can be: id, potential_yield
    'square_text': 'potential_yield',  

    # Log specifics of how each square is determined valid
    'log_all_valid': False             
}

AI_DEBUG = False
AI_DEBUG_SETTINGS = {
    # print the relevant calculations, if any, done by the AI to calculate its move
    'show_calcs': False,

    # print a log of all moves at end of game
    'show_history': True
}

#==================================================#

class Board:
    def __init__(self):
        self.__data = []
    
    def append(self, item):
        self.__data.append(item)


    def get_square(self, square_id):
        return self.__data[square_id]


    def get_squares(self, slice):
        return self.__data[slice]


    @property
    def data(self):
        return self.__data

    @property
    def turn_number(self):
        global turn_counter
        return turn_counter

    def update(self, current_player):
        '''
        Recalculates valid squares (dark green squares) based on the given color

        current_player: the color to calculate for
        '''

        for square in self:

            if square["background"] == 'dark olive green': # if dark green set to green
                square.configure(bg='green')        

            # find new valid green squares and color them dark olive green
            if square.color not in ['white', 'black']:
                if square.is_valid(current_player):
                    square['state'] = 'normal'
                    square.configure(bg='dark olive green')
                else:
                    square['state'] = 'disabled' # disable unplayable squares

                
            square.configure(command= partial(square.take_turn, current_player))

        # if no moves available, enable all squares
        if len([square for square in self if square['state'] == 'normal']) == 0:
            for square in self:
                if square['background'] == 'green':
                    square['background'] = 'dark olive green'
                    square['state'] = 'normal'

        # show updated potential yields in debug
        if DEBUG and DEBUG_SETTINGS['square_text'] == 'potential_yield':
            for square in self:
                if square['background'] == 'dark olive green':
                    square.configure(text=square.potential_yield, font=("Courier", 20)) # show potential yield of squares
                else:
                    square.configure(text='')
        

        # update text
        global turn_text, scoreboard, scoreboard_text
        turn_text.configure(text=f"{current_player}'s turn")
        scoreboard['black'] = math.floor(len([square for square in board if square.color == 'black'])/64 * 100)
        scoreboard['white'] = math.floor(len([square for square in board if square.color == 'white'])/64 * 100)
        scoreboard_text.configure(text=f"Black: {scoreboard['black']}%    White: {scoreboard['white']}% ") 



    def __iter__(self):
        return (square for square in self.__data)

    def __repr__(self):
        return self.__data
        

    __str__ = __repr__


class Square(tk.Button):

    def __init__(self, master, id):
        master = master
        super().__init__(master)
        self.configure(bg='green') # board color
        self.color = None
        self.id = id
        self.potential_yield = 1

        
        ##### DEBUG #####
        if DEBUG:
            if DEBUG_SETTINGS['square_text'] == 'id':
                self.configure(text=self.id, font=("Courier", 20)) # show ID of squares


    def place_chip(self, current_player):
        self['state'] = 'disabled'             # disable self (each square can only be clicked once)
        self.color = current_player            # change to appropriate color
        self.configure(bg=self.color)

        # flip squares
        rays_to_flip = self.is_valid(current_player)
        for flip_ray in rays_to_flip:

            indices = flip_ray['indices']
            num_flips = flip_ray['num_flips']
            if flip_ray['reverse']: # some indexes need to be reversed based on direction of the ray
                old_step = indices.step
                if old_step == None:
                    indices = slice(indices.stop - 1, indices.start, -1)
                else:
                    indices = slice(indices.stop - old_step, indices.start, -1 * old_step)

            squares_to_flip = board.get_squares(indices)[:num_flips]

            
            for square in squares_to_flip:
                square.flip()
                # log flips in debug
                if DEBUG:
                    print(f'flipping {square} to {current_player}')
                


    # called on square click
    def take_turn(self, color):
        global turn_counter, turn_text, current_player, scoreboard, scoreboard_text, board

        def is_game_over(turn_counter):
            # check for end of game
            colors = [square['background'] for square in board]
            if 'green' not in colors and 'dark olive green' not in colors:
                if LOG_TURNS:
                    print('\n---------- END OF GAME ------------')
                if scoreboard['black'] > scoreboard['white']:
                    winner = 'black'
                else:
                    winner = 'white'
                
                turn_text.configure(text=f'{winner} wins!') 

                if AI_DEBUG and AI_DEBUG_SETTINGS['show_history']:
                    try:
                        print('\nAI PLAYER 1 HISTORY\n')
                        for turn in ai_black.history:
                            print(turn)
                        print('\n-----------------------------')
                    except:
                        pass # ai_black doesn't exist

                    print('\nAI PLAYER 2 HISTORY\n')
                    for turn in ai_white.history:
                        print(turn)
                
                return True
            return False

        turn_counter += 1

        if NUM_PLAYERS > 0:
            if self['state'] != 'disabled': # check if the square is clickable
                if LOG_TURNS:
                    print(f'\n--- TURN {turn_counter} ({current_player}) ---')
                    print(f'{current_player} plays <Square {self.id}>')
                self.place_chip(current_player)
                
                # change to other player
                change_player()

                # determine new valid spaces on board
                board.update(current_player)

                # AI takes turn if there is only 1 human player
                if NUM_PLAYERS == 1:
                    turn_counter += 1
                    if LOG_TURNS:
                        print(f'\n--- TURN {turn_counter} ({current_player}) (AI) ---')
                    
                    ai_white.take_turn(board, current_player) # Call AI

                    change_player()

                    board.update(current_player)

                # check for end of game
                is_game_over(turn_counter)

        ##### FOR TRAINING ######
        else:
            while not is_game_over(turn_counter):
                
                ##### AI 1
                turn_counter += 1
                if LOG_TURNS:
                    print(f'\n--- TURN {turn_counter} ({current_player}) (AI) ---')
                
                if FIRST_AI == 'black':
                    ai_black.take_turn(board, current_player) # Call AI
                else:
                    ai_white.take_turn(board, current_player)
                change_player()

                board.update(current_player)

                ##### AI 2
                turn_counter += 1
                if LOG_TURNS:
                    print(f'\n--- TURN {turn_counter} ({current_player}) (AI) ---')
                
                if FIRST_AI == 'white':
                    ai_white.take_turn(board, current_player) # Call AI
                else:
                    ai_black.take_turn(board, current_player)

                change_player()

                board.update(current_player)
            
            master.quit() # close tkinter window
            
            

    def flip(self):
        if self.color == 'black':
            self.color = 'white'
        else:
            self.color = 'black'
        self.configure(bg=self.color)
    

    def is_valid(self, current_player):
        '''
            Determines if the square is a valid space with respect to the given player. Returns a list of all rays or a Falsy object ([])
        '''

        def get_rays():

            # colors in each direction away from current square
            def get_colors(slice, reverse=False, name=None):
                colors = [sq.color for sq in board.get_squares(slice)]
                for i, color in enumerate(colors):
                    if not color:
                        colors[i] = 'blank'
                if reverse:
                    colors = colors[::-1]
                return {
                    'slice': slice,
                    'colors': colors,
                    'reverse': reverse,
                    'name': name
                    }

            # up down left right
            r_n = get_colors(slice(self.id % 8, self.id, 8), reverse=True, name='North')
            r_s = get_colors(slice(self.id+8, self.id % 8 + 64, 8), name='South')
            r_e = get_colors(slice(self.id+1, self.id + (8 - self.id % 8)), name='East')
            r_w = get_colors(slice(8 * (self.id // 8), self.id), reverse=True, name='West')

            # lambda functions to calculate how far from edge
            num_left = lambda id: id % 8
            num_right = lambda id: 7 - (id % 8)
            num_up = lambda id: (id // 8)
            num_down = lambda id: 7 - (id // 8)

            # diagonal endpoints
            end_nw = self.id - (9 * min(num_left(self.id), num_up(self.id)))
            end_ne = self.id - (7 * min(num_right(self.id), num_up(self.id)))
            end_sw = self.id + (7 * min(num_left(self.id), num_down(self.id)))
            end_se = self.id + (9 * min(num_right(self.id), num_down(self.id)))
            
            r_nw = get_colors(slice(end_nw, self.id, 9), reverse=True, name='Northwest')
            r_ne = get_colors(slice(end_ne, self.id, 7), reverse=True, name='Northeast')
            r_sw = get_colors(slice(self.id+7, end_sw+7, 7), name='Southwest')
            r_se = get_colors(slice(self.id+9, end_se+9, 9), name='Southeast')

            return [r_n, r_s, r_e, r_w, r_nw, r_ne, r_se, r_sw]
        

        rays = get_rays()
        
        ray_indexes_with_flips = [] # each ray's slice object and num of flips (ie flip the first X squares in this sequence of indexes)
        for ray in rays:
            ray_str = ''.join([color for color in ray['colors']])
            if current_player == 'black':
                my_match = re.match(pattern='^(white)+(black)', string=ray_str)
            elif current_player == 'white':
                my_match = re.match(pattern='^(black)+(white)', string=ray_str)

            if my_match:
                # determine number of squares in ray to flip
                
                colors_in_flip_ray = my_match.group()
                len_flip_ray = colors_in_flip_ray.count('white') + colors_in_flip_ray.count('black')
                num_flips = len_flip_ray - 1

                if DEBUG and DEBUG_SETTINGS['log_all_valid']:
                    print(f"{self.id} - {num_flips} flip{'s'*bool(self.potential_yield>1)} {ray['name']}")

                ray_indexes_with_flips.append(
                    {
                    'starting_index': self.id, 
                    'indices': ray['slice'], 
                    'num_flips': num_flips, 
                    'reverse': ray['reverse']
                    })

                self.potential_yield =  sum([ray['num_flips'] for ray in ray_indexes_with_flips if ray['starting_index'] == self.id]) # how many points you could get off of flipping this square

        return ray_indexes_with_flips


    def __repr__(self):
        return f'<Square {self.id}>'
    

    __str__ = __repr__


def change_player():
    global current_player
    if current_player =='black':
        current_player = 'white'
    elif current_player =='white':
        current_player = 'black'

def setup(starting_player):

    global turn_text, scoreboard_text, scoreboard, ai_black, ai_white, turn_counter

    turn_counter = 0
    board = Board() # the game manager
    master = tk.Tk()
    master.resizable(False, False)
    container = tk.Frame(master)  # for padding
    container.pack(padx=10, pady=10)

    # title
    font_title = tkFont.Font(family="Lucida Grande", size=30)
    tk.Label(container, text="Othello", font=font_title).pack()
    
    font_turn = tkFont.Font(family="Lucida Grande", size=20)
    turn_text = tk.Label(container, text=f"{starting_player}'s turn", font=font_turn)
    turn_text.pack()

    font_scoreboard = tkFont.Font(family="Lucida Grande", size=15)
    scoreboard_text = tk.Label(container, text=f"Black: {scoreboard['black']}%    White: {scoreboard['white']}% ", font=font_scoreboard)
    scoreboard_text.pack()

    # board
    board_frame = tk.Frame(container)
    board_frame.pack()

    
    if starting_player == 'black':
        first_valid_squares = [20, 29, 34, 43] # starting valid ids for black
    else:
        first_valid_squares = [19, 28, 37, 44] # starting valid ids for white

    # buttons
    square_id = 0
    for x in range(8):
        for y in range(8):

            # Frame setup
            frame = tk.Frame(board_frame, width=60, height=60) #their units in pixels
            frame.grid_propagate(False) #disables resizing of frame
            frame.columnconfigure(0, weight=1) #enables button to fill frame
            frame.rowconfigure(0,weight=1) #any positive number would do the trick
            frame.grid(row=x, column=y) #put frame where the button should be

            # Square setup
            square = Square(frame, square_id)
            square.configure(command= partial(square.take_turn, 'black'), activebackground="dark green")
            square.grid(sticky="wens") #makes the button expand
            
            board.append(square) # add square to board

            # middle 4 squares
            if square_id in [27, 36]:
                square.color = 'black'
                square.configure(bg=square.color)
                square['state'] = 'disabled'
            elif square_id in [28, 35]:
                square.color = 'white'
                square.configure(bg=square.color)
                square['state'] = 'disabled'
            
            
            # enable/disable squares for first move
            if square_id not in first_valid_squares:
                square['state'] = 'disabled'
            else:
                square['state'] = 'normal'
                square.configure(bg='dark olive green')
            
            square_id += 1

    ##### setup AI ######

    if NUM_PLAYERS == 0:
        if AI_MAPPING == {}:
            raise BaseException('Please enter an AI mapping.')

        ai_black = AIOthello('black', debug=AI_DEBUG, debug_settings=AI_DEBUG_SETTINGS, method=AI_MAPPING['black'], logging=LOG_TURNS)
        ai_white = AIOthello('white', debug=AI_DEBUG, debug_settings=AI_DEBUG_SETTINGS, method=AI_MAPPING['white'], logging=LOG_TURNS)
    
    elif NUM_PLAYERS == 1:
        if current_player == 'black':
            ai_white_color = 'white'
        else:
            ai_white_color = 'black'
        ai_white = AIOthello(ai_white_color, debug=AI_DEBUG, debug_settings=AI_DEBUG_SETTINGS, method='highest_yield', logging=LOG_TURNS)


    return board, master


################### DRIVER CODE ######################

# globals
current_player = STARTING_PLAYER
FIRST_AI = 'black'
AI_MAPPING = {}
board = None
master = None
if NUM_PLAYERS == 0:
    ai_black = None
    ai_white = None
elif NUM_PLAYERS == 1:
    ai_white = None

turn_text = None
scoreboard_text = None
turn_counter = 0
scoreboard = { # percentage of the board
    'black': 3, # 2 starting squares // 64 = 3%
    'white': 3
}

def play(num_players, starting_player='black', first_ai='black', ai_mapping={}):
    global board, master, current_player, STARTING_AI, NUM_PLAYERS, FIRST_AI, AI_MAPPING

    NUM_PLAYERS = num_players
    FIRST_AI=first_ai
    AI_MAPPING = ai_mapping
    current_player = starting_player
    board, master = setup(starting_player=current_player)

    if NUM_PLAYERS == 0:
        def start_ai_game():
            # start game with random valid square
            if current_player == 'black':
                board.get_square(random.choice([21, 30, 35, 44])).take_turn('black')
            else:
                board.get_square(random.choice([20, 27, 38, 45])).take_turn('white')

        master.after(10, start_ai_game)

    if not SHOW_GUI:
        master.withdraw()
    master.mainloop()
    
    winner = turn_text["text"][:5]
    if LOG_TURNS:
        print(f'{winner} wins!')
    return winner, master


play(1)