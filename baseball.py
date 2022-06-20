from scrape import ScrapeSR
from objects import Team
import itertools
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
import random
sns.set()
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

'''
    - take starters out in the 7th and cycle through relievers
    - make it work on college and minor leagues too
    - total run dirrerential
    - double plays
    - run differential
    - lineup optimizer
    - situational
    - factor positions into lineup construction (split position groups into different lists, pick the ones that do the best against certain pitchers, then see which order of those players is most optimal)
'''

class Baseball():

    def __init__(self):
        self.LEVEL = input('\nENTER LEVEL OF COMPETITION (mlb or other): ').title().strip()

        if self.LEVEL.lower() == 'other':
            self.league = input('\nENTER LEAGUE NAME: ').title().strip()


        opt = input('\nWOULD YOU LIKE TO USE THE LINEUP OPTIMIZER? (y/n): ')
        if opt.strip().lower() == 'y':
            self.TEAM1 = input('\nENTER YOUR TEAM: ').title().strip()
            self.TEAM2 = input('ENTER TEAM WHO THEY ARE FACING: ').title().strip()
            self.vis = 'n'

            if self.LEVEL.lower() == 'other':
                scraper = ScrapeSR('Baseball', self.league, self.TEAM1, self.TEAM2, self.LEVEL)
                
            elif self.LEVEL.lower() == 'mlb':
                scraper = ScrapeSR('Baseball', 'mlb', self.TEAM1, self.TEAM2, self.LEVEL)

            self.team1hit = scraper.hit1
            self.team2hit = scraper.hit2
            self.team1pit = scraper.pit1
            self.team2pit = scraper.pit2

            Team1 = Team(self.team1hit, self.team1pit, scraper, self.TEAM1, 'red', 'auto')
            Team2 = Team(self.team2hit, self.team2pit, scraper, self.TEAM2, 'blue', 'auto')

            print('\n')
            for pitcher in Team2.pitchers:
                if pitcher.weird == False:
                    print(pitcher.Name)

            pitcher_name = input(f'\nSELECT WHICH PITCHER THE {self.TEAM1} ARE FACING: ').strip()
            opitcher = [pitcher for pitcher in Team2.pitchers if pitcher.Name == pitcher_name]
            self.OptLineup(Team1.batting_roster, opitcher[0])


        elif opt.strip().lower() == 'n':
            self.TEAM1 = input('\nENTER TEAM 1: ').title().strip()
            self.TEAM2 = input('ENTER TEAM 2: ').title().strip()
            self.lineup_settings = input('\nLINEUP SETTINGS (manual/auto): ').strip().lower()
            self.num_sims = int(input('\nENTER NUMBER OF SIMULATIONS: ').strip())

            self.vis = input('\nVISUALIZE PLAY BY PLAY? (y/n): ').strip().lower()

            if self.LEVEL.lower() == 'other':
                scraper = ScrapeSR('Baseball', self.league, self.TEAM1, self.TEAM2, self.LEVEL)
                
            elif self.LEVEL.lower() == 'mlb':
                scraper = ScrapeSR('Baseball', 'mlb', self.TEAM1, self.TEAM2, self.LEVEL)

            self.team1hit = scraper.hit1
            self.team2hit = scraper.hit2
            self.team1pit = scraper.pit1
            self.team2pit = scraper.pit2

            Team1 = Team(self.team1hit, self.team1pit, scraper, self.TEAM1, 'red', self.lineup_settings)
            Team2 = Team(self.team2hit, self.team2pit, scraper, self.TEAM2, 'blue', self.lineup_settings)

            # self.num_sims = int(input('\nENTER NUMBER OF SIMULATIONS: '))
            # so they play equal home / road games
            games = 0
            t1i = 0
            t2i = 0
            for i in range(self.num_sims // 2):
                    if t1i == len(Team1.rotation):
                        t1i = 0
                    if t2i == len(Team2.rotation):
                        t2i = 0
                    self.game(Team1, Team2, Team1.lineup, Team2.lineup, Team1.rotation[t1i], Team2.rotation[t2i])
                    t1i += 1
                    t2i += 1
                    games += 1
                    if self.vis == 'y':
                        plt.scatter(games, Team1.wins, marker = 'o', c = Team1.color, alpha = .25)
                        plt.scatter(games, Team2.wins, marker = 'o', c = Team2.color, alpha = .25)
            t2i = 0
            t1i = 0
            for i in range(self.num_sims // 2):
                if t1i == len(Team1.rotation):
                    t1i = 0
                if t2i == len(Team2.rotation):
                    t2i = 0
                self.game(Team2, Team1, Team2.lineup, Team1.lineup, Team2.rotation[t2i], Team1.rotation[t1i])
                t1i += 1
                t2i += 1
                games += 1
                if self.vis == 'y':
                    plt.scatter(games, Team1.wins, marker = 'o', c = Team1.color, alpha = .25)
                    plt.scatter(games, Team2.wins, marker = 'o', c = Team2.color, alpha = .25)

            self.summary(Team1, Team2)

        ''' -------------------------------- Baseball Game Functions ------------------------------------- '''
    def PA(self, hitter, pitcher):
        result = random.choices(['K', 'BB', 'H', 'IPO', 'HBP'], weights = (hitter.Kp + pitcher.Kp, hitter.BBp + pitcher.BBp, hitter.Hp + pitcher.Hp, hitter.IPOp + pitcher.IPOp, hitter.HBPp + pitcher.HBPp))
        hitter.PA += 1
        pitcher.BF += 1

        if result != 'HBP' and result != 'BB':
            hitter.AB += 1

        return result[0]

    def clear_bases(self, base_state):
        for i in range(len(base_state)):
            base_state[i] = None
        return base_state

    def advance_bases(self, base_state, play_result, hitter, pitcher):
        runs_scored_on_play = 0
        bases_occupied = []
        for base in base_state:
            if base != None:
                bases_occupied.append(base_state.index(base) + 1)

        # if there is a homerun
        if play_result == 'HR':
            runs_scored_on_play += (1 + len(bases_occupied))
            base_state = self.clear_bases(base_state)
            if self.vis == 'y':
                print(f'{hitter.Name} hits a {1 + len(bases_occupied)} run BOMB off of {pitcher.Name}')

        elif play_result == '3B':
            runs_scored_on_play += len(bases_occupied)
            base_state[2] = hitter

        # only one runner on
        elif play_result != 'HR' and play_result != '3B':
            # no runners on
            if len(bases_occupied) == 0:
                if play_result == 'BB' or play_result == 'HBP':
                    base_state[0] = hitter
                elif play_result == '1B':
                    base_state[0] = hitter
                elif play_result == '2B':
                    base_state[1] = hitter
            # one runner on
            elif len(bases_occupied) == 1:
                if sum(bases_occupied) == 1: # runner on 1st
                    if play_result == 'BB' or play_result == 'HBP':
                        base_state[1] = base_state[0]
                        base_state[0] = hitter
                    elif play_result == '1B':
                        base_state[1] = base_state[0]
                        base_state[0] = hitter
                    elif play_result == '2B':
                        runs_scored_on_play += 1
                        base_state[1] = hitter
                        base_state[0] = None
                elif sum(bases_occupied) == 2: # runner on 2nd
                    if play_result == 'BB' or play_result == 'HBP':
                        base_state[0] = hitter
                    elif play_result == '1B':
                        base_state[2] = base_state[1]
                        base_state[0] = hitter
                        base_state[1] = None
                    elif play_result == '2B':
                        runs_scored_on_play += 1
                        base_state[1] = hitter
                elif sum(bases_occupied) == 3: # runner on third base
                    if play_result == 'BB' or play_result == 'HBP':
                        base_state[0] = hitter
                    elif play_result == '1B':
                        base_state[0] = hitter
                        runs_scored_on_play += 1
                        base_state[2] = None
                    elif play_result == '2B':
                        base_state[1] = hitter
                        base_state[2] = None
                        runs_scored_on_play += 1
            # two runners on
            elif len(bases_occupied) == 2:
                if sum(bases_occupied) == 3: # first and second
                    if play_result == 'BB' or play_result == 'HBP':
                        base_state[2] = base_state[1]
                        base_state[1] = base_state[0]
                        base_state[0] = hitter
                    elif play_result == '1B':
                        base_state[2] = base_state[1]
                        base_state[1] = base_state[0]
                        base_state[0] = hitter
                    elif play_result == '2B':
                        runs_scored_on_play += 1
                        base_state[2] = base_state[1]
                elif sum(bases_occupied) == 5: # second and third
                    if play_result == 'BB' or play_result == 'HBP':
                        base_state[0] = hitter
                    elif play_result == '1B':
                        runs_scored_on_play += 1
                        base_state[2] = base_state[1]
                        base_state[1] = None
                        base_state[0] = hitter
                    elif play_result == '2B':
                        runs_scored_on_play += 2
                        base_state[1] = hitter
                        base_state[2] = None
                elif sum(bases_occupied) == 4: # first and third
                    if play_result == 'BB' or play_result == 'HBP':
                        base_state[1] = base_state[0]
                        base_state[0] = hitter
                    elif play_result == '1B':
                        if self.vis == 'y':
                            print(f'{base_state[2].Name} scores after {hitter.Name} {play_result}')
                        runs_scored_on_play += 1
                        base_state[2] = None
                        base_state[1] = base_state[0]
                        base_state[0] = hitter
                    elif play_result == '2B':
                        if self.vis == 'y':
                            print(f'{base_state[2].Name} and {base_state[0].Name} scores after {hitter.Name} {play_result}')
                        runs_scored_on_play += 2
                        base_state[1] = hitter
                        base_state[0] = None
                        base_state[2] = None
            # bases loaded (3 runners on)
            elif len(bases_occupied) == 3:
                if play_result == 'BB' or play_result == 'HBP':
                    if self.vis == 'y':
                        print(f'{base_state[2].Name} scores after {hitter.Name} {play_result}')
                    runs_scored_on_play += 1
                    base_state[2] = base_state[1]
                    base_state[1] = base_state[0]
                    base_state[0] = hitter
                elif play_result == '1B':
                    if self.vis == 'y':
                        print(f'{base_state[2].Name} scores after {hitter.Name} {play_result}')
                    runs_scored_on_play += 1
                    base_state[2] = base_state[1]
                    base_state[1] = base_state[0]
                    base_state[0] = hitter
                elif play_result == '2B':
                    runs_scored_on_play += 2
                    if self.vis == 'y':
                        print(f'{base_state[2].Name} and {base_state[1].Name} scores after {hitter.Name} {play_result}')
                    base_state[2] = base_state[0]
                    base_state[1] = hitter
                    base_state[0] = None
        hitter.RBI += runs_scored_on_play
        pitcher.ER += runs_scored_on_play
        return base_state, runs_scored_on_play

    def half_inning(self, lineup, current_batsman_index, pitcher, hitting_team_score, visualize = 'n'):
        index = current_batsman_index
        runs_scored = 0
        # base_state = base_state
        # base_stase = self.clear_bases(base_state)
        base_state = [None, None, None]
        outs = 0
        results = []

        if current_batsman_index >= len(lineup):
            index = 0

        while outs < 3:

            result = self.PA(lineup[index], pitcher)   

            if visualize == 'y':
                print(f'{lineup[index].team} {index + 1} {lineup[index].Name} {result}')

            # check if there was an out
            if result == 'IPO':
                lineup[index].IPO += 1
                index += 1
                results.append(result)
                outs += 1
            elif result == 'K':
                lineup[index].K += 1
                pitcher.K += 1
                index += 1
                results.append('K')
                outs += 1

            # then if it was something else
            elif result == 'HBP':
                base_state, scored = self.advance_bases(base_state, result, lineup[index], pitcher)
                runs_scored += scored
                pitcher.HBP += 1
                results.append(result)
                lineup[index].HBP += 1
                index += 1
            elif result == 'BB':
                base_state, scored = self.advance_bases(base_state, result, lineup[index], pitcher)
                runs_scored += scored
                results.append(result)
                pitcher.BB += 1
                lineup[index].BB += 1
                index += 1
            elif result == 'H':
                pitcher.H += 1
                lineup[index].H += 1
                # then determine what kind of hit it is
                hit_type = random.choices(['1B', '2B', '3B', 'HR'], (lineup[index].singlep, lineup[index].doublep, lineup[index].triplep, lineup[index].HRp))[0]
                if hit_type == '1B':
                    base_state, scored = self.advance_bases(base_state, hit_type, lineup[index], pitcher)
                    runs_scored += scored
                    results.append(hit_type)
                    lineup[index].singles += 1
                    pitcher.singles += 1
                    index += 1
                elif hit_type == '2B':
                    base_state, scored = self.advance_bases(base_state, hit_type, lineup[index], pitcher)
                    runs_scored += scored
                    results.append(hit_type)
                    lineup[index].doubles += 1
                    pitcher.doubles += 1
                    index += 1
                elif hit_type == '3B':
                    base_state, scored = self.advance_bases(base_state, hit_type, lineup[index], pitcher)
                    runs_scored += scored
                    results.append(hit_type)
                    lineup[index].triples += 1
                    pitcher.triples += 1
                    index += 1
                elif hit_type == 'HR':
                    base_state, scored = self.advance_bases(base_state, hit_type, lineup[index], pitcher)
                    runs_scored += scored
                    results.append(hit_type)
                    lineup[index].HR += 1
                    pitcher.HR += 1
                    index += 1

            if index >= len(lineup):
                index = 0
        pitcher.IP += 1
        return runs_scored, index, results

    def game(self, team1, team2, lineup1, lineup2, pitcher1, pitcher2, situation = False):
        team1Score = 0
        team2Score = 0
        next_lineup1_list = [0]
        next_lineup2_list = [0]
        results = []

        if situation == False:

            for i in range(9):
                next_in_line1 = next_lineup1_list[-1]
                runs, new_lineup_index, half_inning_sequence  = self.half_inning(lineup1, next_in_line1, pitcher2, team1Score, visualize = self.vis)
                next_lineup1_list.append(new_lineup_index)
                results.append(half_inning_sequence)
                team1Score += runs

                next_in_line2 = next_lineup2_list[-1]
                runs, new_lineup_index, half_inning_sequence = self.half_inning(lineup2, next_in_line2, pitcher1, team2Score, visualize = self.vis)
                next_lineup2_list.append(new_lineup_index)
                results.append(half_inning_sequence)
                team2Score += runs

            ''' check the results list so we can track sequences and look for things like shutouts, 3k innings, back 2 back homers '''
            # seems a little complicated, try later
            # # extras
            # if team1Score == team2Score:
            #     while team1Score == team2Score:
            #         runs = self.half_inning(team1Score)
            #         team1Score += runs

            #         runs = self.half_inning(team2Score)
            #         team2Score += runs

            if team1Score > team2Score:
                    team1.wins += 1
                    if self.vis == 'y':
                        print(f'\nTHE {team1.name} WIN!')
                        print(f'SCORE: {team1Score} to {team2Score}')
                    team2.losses += 1
            elif team1Score < team2Score:
                if self.vis == 'y':
                    print(f'\nTHE {team2.name} WIN!')
                    print(f'SCORE: {team1Score} to {team2Score}')
                team1.losses += 1
                team2.wins += 1
                # while we still do not have extra innings done yet
            elif team1Score == team2Score:
                if self.vis == 'y':
                    print(f'\nTIE (working on extra innings)')
                    print(f'SCORE: {team1Score} to {team2Score}')
                team1.draws += 1
                team2.draws += 1
            if self.vis == 'y':
                print(f'\n{team1.name} wins, losses, ties: {team1.wins} {team1.losses} {team1.draws}')
                print(f'{team2.name} wins, losses, ties: {team2.wins} {team2.losses} {team2.draws}\n\n')

    
    ''' -------------------------- Summary Functions -----------------------------'''

    def summary(self, team1, team2):
        print('\n')
        for i in range(9):
            print('-', end = ' ')
        print('RESULTS', end = ' ')
        for i in range(10):
            print('-', end = ' ')
        print('\n')
        # call the rate stats function on all players
        print(f'\n{team1.name} lineup:')
        for hitter in team1.lineup:
            if hitter.PA > 0 and hitter.H > 0:
                hitter.rate_stats()
        print('\n')
        print(f'{team1.name} pitchers:')
        for pitcher in team1.rotation:
            if pitcher.IP > 0:
                pitcher.rate_stats()
        print('\n')
        print(f'{team2.name} lineup:')
        for hitter in team2.lineup:
            if hitter.PA > 0 and hitter.H > 0:
                hitter.rate_stats()
        print('\n')
        print(f'{team2.name} pitchers')
        for pitcher in team2.rotation:
            if pitcher.IP > 0:
                pitcher.rate_stats()
        print('\n')
        print('\n\nWIN PROBABILITY')
        print(f'In {team1.wins + team1.losses + team1.draws} simulated games...')
        print(f'\n{team1.name}: {(team1.wins / (team1.wins + team1.losses + team1.draws)) * 100:.2f}%')
        print(f'{team2.name}: {(team2.wins / (team2.wins + team2.losses + team2.draws)) * 100:.2f}%\n')
        print(f'EXCLUDING THE {team1.draws} TIES')
        print(f'{team1.name}: {(team1.wins / (team1.losses + team1.wins)) * 100:.2f}%')
        print(f'{team2.name}: {(team2.wins / (team2.losses + team2.wins)) * 100:.2f}%\n')
        print(f'\n{team1.name} Record: {team1.wins} - {team1.losses} - {team1.draws}')
        print(f'{team2.name} Record: {team2.wins} - {team2.losses} - {team2.draws}')
        if self.vis == 'y':
            plt.title(f'{team1.name} ({team1.color}) vs. {team2.name} ({team2.color})')
            plt.xlabel('Games')
            plt.ylabel('Wins')
            plt.show()

    def OptLineup(self, team_roster, opposing_pitcher):
        NUM = int(input('\nNUMBER OF SIMULATIONS PER LINEUP: '))
        combos = list(itertools.combinations(team_roster, 9))
        print(f"\nTESTING ALL {len(combos)} POSSIBLE LINEUP COMBINATIONS ({NUM * len(combos)} total baseball games)...\n")
        lineup_scores = []

        for combo in tqdm(combos):
            team1Score = 0
            for j in range(NUM):
                next_lineup1_list = [0]
                results = []
                # play half innings
                # find which one scored the most runs
                for i in range(9):
                    next_in_line1 = next_lineup1_list[-1]
                    runs, new_lineup_index, half_inning_sequence  = self.half_inning(combo, next_in_line1, opposing_pitcher, team1Score, visualize = 'n')
                    next_lineup1_list.append(new_lineup_index)
                    results.append(half_inning_sequence)
                    team1Score += runs
            lineup_scores.append([team1Score, combo])
        # print(lineup_scores)
        # sort the lineups by score
        best_lineup = sorted(lineup_scores, key = lambda x: x[0])
        print(len(best_lineup))
        print(len(best_lineup[0]))
        print(len(best_lineup[1]))
        print(best_lineup[0][0])
        print(best_lineup[-1][0])
        print('\n - - IDEAL LINEUP - -')
        i = 1
        for player in best_lineup[-1][1]:
                print(str(i) + ' ' + player.Name)
                i += 1

        print(f'\nScored {best_lineup[-1][0] / NUM:.2f} runs per game in {NUM} games versus {opposing_pitcher.Name}')
