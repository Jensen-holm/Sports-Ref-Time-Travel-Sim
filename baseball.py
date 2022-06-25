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
from statistics import median, mode

'''
TO DO LIST
    - visualize why the lineup optimizer makes sense (why is does the best lineup score the most runs?)
    - add an option to select pitchers, but auto lineup the lineup
    - take starters out in the 7th and cycle through relievers
    - make it work on college and minor leagues too
    - double plays
    - analyzing sequence of events
    - situational
    - lefty righty splits
    - extra innings rule
    - base running probability
    - track cool stats
'''

class Baseball():

    def __init__(self):
        self.LEVEL = input('\nENTER LEVEL OF COMPETITION (mlb or other): ').title().strip()

        if self.LEVEL.lower() == 'other':
            self.league = input('\nENTER LEAGUE NAME: ').title().strip()

        opt = input('\nWOULD YOU LIKE TO USE THE LINEUP OPTIMIZER? (y/n): ').strip()
        if opt.strip().lower() == 'y':
            self.TEAM1 = input('\nENTER YOUR TEAM (ex: 2001 Seattle Mariners): ').title().strip()
            self.TEAM2 = input('ENTER THEIR TEAM (ex: 1899 Cleveland Spiders): ').title().strip()
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

            pitcher_name = input(f'\nSELECT WHICH PITCHER THE {self.TEAM1} ARE FACING: ').title().strip()
            opitcher = [pitcher for pitcher in Team2.pitchers if pitcher.Name == pitcher_name]
            self.OptLineup(Team1.batting_roster, opitcher[0])

        elif opt.strip().lower() == 'n':
            self.TEAM1 = input('\nENTER TEAM 1 (ex: 1916 Pliladelphia Athletics): ').title().strip()
            self.TEAM2 = input('ENTER TEAM 2(ex: 2013 Cincinnati Reds): ').title().strip()
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
            self.extra_inning_games = 0
            # append final scores and how many innings it took to this list for further exploration
            self.game_scores = []
            self.other_stats = []

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

    def half_inning(self, lineup, current_batsman_index, pitcher, visualize = 'n'):
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

    def game(self, team1, team2, lineup1, lineup2, pitcher1, pitcher2):
        team1Score = 0
        team2Score = 0
        next_lineup1_list = [0]
        next_lineup2_list = [0]
        results = []


        for i in range(9):
                next_in_line1 = next_lineup1_list[-1]
                runs, new_lineup_index, half_inning_sequence  = self.half_inning(lineup1, next_in_line1, pitcher2, visualize = self.vis)
                next_lineup1_list.append(new_lineup_index)
                results.append(half_inning_sequence)
                team1Score += runs

                next_in_line2 = next_lineup2_list[-1]
                runs, new_lineup_index, half_inning_sequence = self.half_inning(lineup2, next_in_line2, pitcher1, visualize = self.vis)
                next_lineup2_list.append(new_lineup_index)
                results.append(half_inning_sequence)
                team2Score += runs
        innings = 9
            # extra innnings
        if team1Score == team2Score:
                self.extra_inning_games += 1
                while team1Score == team2Score:

                    runs1, new_lineup_index, half_inning_sequence1 = self.half_inning(lineup1, next_in_line1, pitcher2, visualize = self.vis)
                    next_lineup1_list.append(new_lineup_index)
                    team1Score += runs1

                    runs2, new_lineup_index, half_inning_sequence2 = self.half_inning(lineup2, next_in_line2, pitcher1, visualize = self.vis)
                    next_lineup2_list.append(new_lineup_index)
                    team2Score += runs2

                    results.append([[half_inning_sequence1], [half_inning_sequence2]])
                    innings += 1

            # determine winner
        if team1Score > team2Score:
                    team1.wins += 1
                    team2.losses += 1
                    if self.vis == 'y':
                        print(f'\nTHE {team1.name} WIN!')
                        print(f'SCORE: {team1Score} to {team2Score}\n')
        elif team1Score < team2Score:
                if self.vis == 'y':
                    print(f'\nTHE {team2.name} WIN!')
                    print(f'SCORE: {team1Score} to {team2Score}\n')
                team1.losses += 1
                team2.wins += 1
            # find the longest game, and most probable scores for each team using this info below
        self.game_scores.append([team1Score, team2Score, innings])
        self.other_stats.append(results)

    ''' -------------------------- Summary Function -----------------------------'''

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
        print('\nWIN PROBABILITY')
        print(f'In {team1.wins + team1.losses} simulated games...')
        print(f'\n{team1.name}: {(team1.wins / (team1.wins + team1.losses)) * 100:.2f}%')
        print(f'{team2.name}: {(team2.wins / (team2.wins + team2.losses)) * 100:.2f}%')
        print(f'\n{team1.name} Record: {team1.wins} - {team1.losses}')
        print(f'{team2.name} Record: {team2.wins} - {team2.losses}')
        print(f'\nExtra inning probability: {(self.extra_inning_games / (team1.wins + team1.losses)) * 100:.3f}%\n')
        # then do most likley scores, average scores and max innings
        mode1 = mode([x[0] for x in self.game_scores])
        mode2 = mode([x[1] for x in self.game_scores])
        print(f'Runs per game for the {team1.name}: {sum([x[0] for x in self.game_scores]) / (team1.wins + team1.losses):.2f}')
        print(f'Runs per game for the {team2.name}: {sum([x[1] for x in self.game_scores]) / (team2.wins + team2.losses):.2f}')
        print(f'\nMedian Score for the {team1.name}: {median([x[0] for x in self.game_scores])} ')
        print(f'Median Score for the {team2.name}: {median([x[1] for x in self.game_scores])}')
        print(f'\nMost common score for the {team1.name}: {mode([x[0] for x in self.game_scores])} ({([x[0] for x in self.game_scores].count(mode1) / len(self.game_scores)) * 100:.2f}%)')
        print(f'Most common score for the {team2.name}: {mode([x[1] for x in self.game_scores])} ({([x[1] for x in self.game_scores].count(mode2)) / len(self.game_scores) * 100:.2f}%)')
        print(f'\nProbability of the {team1.name} shutting out the {team2.name}: {([x[1] for x in self.game_scores].count(0) / len(self.game_scores)) * 100:.2f}%')
        print(f'Probability of the {team2.name} shutting out the {team1.name}: {([x[0] for x in self.game_scores].count(0) / len(self.game_scores)) * 100:.2f}%')
        print(f'\nLongest game (currently no extra innings rule): {max([x[2] for x in self.game_scores])} innings!\n')


        # track cool numbers
                                                        #   game 1                             game 2
        # other stats list is structured like [ [ [half_inning], [half_inning] ], [ [half_inning], [half_inning] ] ]
        # walks = []
        # hbps = []
        # ks = []
        # hits = []

        # perfect_games = 0
        # no_hitters = 0

        # for game in self.other_stats:
        #     for half_inning in game:
        #         if

        # then make the graph


        if self.vis == 'y':
            plt.title(f'{team1.name} ({team1.color}) vs. {team2.name} ({team2.color})')
            plt.xlabel('Games')
            plt.ylabel('Wins')
            plt.show()

        ''' ------------------- Lineup Optimizer ------------------'''
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
                for i in range(9):
                    next_in_line1 = next_lineup1_list[-1]
                    runs, new_lineup_index, half_inning_sequence  = self.half_inning(combo, next_in_line1, opposing_pitcher, team1Score)
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
