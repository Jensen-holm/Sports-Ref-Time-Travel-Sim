import itertools
from multiprocessing.sharedctypes import Value
from tqdm import tqdm

'''
TO DO:
 - give situational lineups the option of saving as the most recent (probably to csv)
   and be able to use old lineups so we do not have to manually set it up every single time
'''

def OptLineup(team_roster, opposing_pitcher, half_inning_func):
        num_sims = int(input('\nNUMBER OF SIMULATIONS PER LINEUP: '))
        combos = list(itertools.combinations(team_roster, 9))
        print(f"\nTESTING ALL {len(combos):,} POSSIBLE LINEUP COMBINATIONS ({num_sims * len(combos):,} total baseball games)...\n")
        lineup_scores = []
        for combo in tqdm(combos):
            team1Score = 0
            for j in range(num_sims):
                next_lineup1_list = [0]
                results = []
                for i in range(9):
                    next_in_line1 = next_lineup1_list[-1]
                    runs, new_lineup_index, half_inning_sequence  = half_inning_func(combo, next_in_line1, opposing_pitcher, vis = 'n')
                    next_lineup1_list.append(new_lineup_index)
                    results.append(half_inning_sequence)
                    team1Score += runs
            lineup_scores.append([team1Score, combo])


        best_lineup = sorted(lineup_scores, key = lambda x: x[0])
        print('\n - - TOP 10 LINEUPS - -')
        for i in range(-1, -11, -1):
            for player in best_lineup[i][1]:
                player.rate_stats()
            print(f'\nScored {best_lineup[i][0] / num_sims:.2f} runs per game in {num_sims} games versus {opposing_pitcher.Name}\n\n')

def Situational_prompt(team1, team2):

    option = input('\nWould you like to use last saved input? (y/n): ').lower().strip()

    if option == 'y':
        print('\nCurrently working on saving and using old input.\n')
        quit()
        # open a txt file, and read what different things are

    else:
        print('\n')
        for team in [team1, team2]:
            print(team.team_name)

    # after user sets lineups manually, prompt to set situation
        home_team_name = input(f'\nSet home team: ').title().strip()
        away_team_name = input(f'Set away team: ').title().strip()

        # match all the input to actual objects
        home_team = [team for team in [team1, team2] if team.team_name == home_team_name]
        away_team = [team for team in [team1, team2] if team.team_name == away_team_name]

        if len(home_team) == 0:
            raise ValueError(f'\n"{home_team_name}" IS NOT A VALID TEAM.')
        elif len(away_team) == 0:
            raise ValueError(f'\n"{away_team_name}" IS NOT A VALID TEAM.')
        else:
            home_team = home_team[0]
            away_team = away_team[0]

        inning = float(input('What inning is it? (ex: 7.5): ').strip())
        outs = int(input('How many outs are there?: ').strip())


        # who is next to bat for each team
        index_home = int(input(f'\nWhat spot in the lineup is up next for the {home_team.team_name}? ').strip())
        index_away = int(input(f'What spot in the lineup is up next for the {away_team.team_name}? ').strip())


    # save input to a txt file in a folder we made called user input

    return home_team, away_team, index_home, index_away, inning, outs

def Situation(team1, team2):

    home_team, away_team, index_home, index_away, inning, outs = Situational_prompt(team1, team2)

    

    return