import random
import sys

class BoardData:
    def __init__(self, data, turn):
        self.data = data
        self.turn = turn
    
    def __repr__(self):
        return f"<BoardData: turn {self.turn}>"


class AIOthello:
    def __init__(self, color, debug=False, method='random', debug_settings={}, logging=True):
        '''
            An AI model to play Othello. Specify the color it is playing.
        '''

        self.color = color
        self.debug = debug
        self.debug_settings = debug_settings
        self.method = method
        self.history = []
        self.logging=logging


    def take_turn(self, board, current_player):
        '''
            takes the current board and returns the index it wants to play
        '''

        valid_square_ids = [square.id for square in board if square['state'] == 'normal']
        # determine move
        methods = {
            'random': self.random_move(valid_square_ids),
            'highest_yield': self.highest_yield_move(valid_square_ids, board)
        }
        square_id = methods[self.method] # run method
            

        chosen_square = board.get_square(square_id)
        chosen_square.place_chip(current_player)

        # build move history if ai debug requires
        if self.debug_settings['show_history']:
            self.history.append({
                'square_id': square_id,
                'board_data': BoardData(board.data, board.turn_number)
            })
        if self.logging:
            print(f'{self.color} (AI) plays <Square {square_id}>')
        return square_id


    def random_move(self, valid_square_ids):
        return random.choice(valid_square_ids)

    
    def highest_yield_move(self, valid_square_ids, board):
        valid_squares_sorted = [board.get_square(id) for id in valid_square_ids]
        valid_squares_sorted.sort(key=lambda x: x.potential_yield, reverse=True)
        highest_yield = valid_squares_sorted[0].potential_yield

        if self.debug and self.debug_settings['show_calcs']:
            print('Potential Yields:')
            [print(x, x.potential_yield) for x in valid_squares_sorted]

        # If there's a tie, choose random square that contains the highest yield
        ocurrences_of_highest_yield = len([square for square in valid_squares_sorted if square.potential_yield == highest_yield])
        square_to_play = random.choice(valid_squares_sorted[:ocurrences_of_highest_yield])
        return square_to_play.id


    def __repr__(self):
        return f'<AIOthello ({self.color})>'

    __str__ = __repr__