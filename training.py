from game import play
import pickle
import random

n = 40 # number of proportions (n)
num_games = 100 # number of games to calculate proportion of wins from
ai_mapping = {
    'black': 'random',
    'white': 'random'
}

black_white_ratios = []

for j in range(n):
    wins_black = 0
    wins_white = 0
    for i in range(num_games):
        first_ai = random.choice(['black', 'white']) ####### The AI 
        winner, master = play(0, first_ai='black', ai_mapping=ai_mapping)
        master.destroy()

        if winner =='black':
            wins_black += 1
        else:
            wins_white += 1

    black_white_ratio = wins_black / num_games
    black_white_ratios.append(black_white_ratio)
    print(f'----- Repetition {j+1} ({black_white_ratio})-----')

print(black_white_ratios)

with open(f'n{n}_games{num_games}_random', 'ab')  as f:
    pickle.dump(black_white_ratios, f)  


