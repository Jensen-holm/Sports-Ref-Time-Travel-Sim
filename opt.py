import itertools
from tqdm import tqdm
from baseball_functions import half_inning

''' ------------------- Lineup Optimizer ------------------'''
def OptLineup(team_roster, opposing_pitcher):
        NUM = int(input('\nNUMBER OF SIMULATIONS PER LINEUP: '))
        combos = list(itertools.combinations(team_roster, 9))
        print(f"\nTESTING ALL {len(combos)} POSSIBLE LINEUP COMBINATIONS ({NUM * len(combos)} total baseball games)...\n")
        lineup_scores = []
        for combo in tqdm(combos):
            team1Score = 0
            for j in range(NUM):
                next_lineup1_list = [0]
                results = []
                for i in range(9):
                    next_in_line1 = next_lineup1_list[-1]
                    runs, new_lineup_index, half_inning_sequence  = half_inning(combo, next_in_line1, opposing_pitcher, team1Score)
                    next_lineup1_list.append(new_lineup_index)
                    results.append(half_inning_sequence)
                    team1Score += runs
            lineup_scores.append([team1Score, combo])

        best_lineup = sorted(lineup_scores, key = lambda x: x[0])
        print('\n - - TOP 10 LINEUPS - -')
        for i in range(-1, -11, -1):
            for player in best_lineup[i][1]:
                player.lineup_rate_stats()
            print(f'\nScored {best_lineup[i][0] / NUM:.2f} runs per game in {NUM} games versus {opposing_pitcher.Name}')