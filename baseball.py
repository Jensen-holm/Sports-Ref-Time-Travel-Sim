from statistics import median, mode
from baseball_functions import half_inning
from scrape import ScrapeSR
from objects import Team
from opt import OptLineup
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

'''
TO DO LIST
    - get probabilities from baseball reference from the detailed splits pages for each player (mlb only)
    - add an option to select pitchers, but auto lineup
    - take starters out in the 7th and cycle through relievers in both manual and auto lineup mode
    - make it work on college and minor leagues too
    - double plays
    - analyzing sequence of events
    - situational analysis
    - lefty righty splits
    - extra innings rule (runner on second)
    - track cooler stats
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
            OptLineup(Team1.batting_roster, opitcher[0])

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

    def game(self, team1, team2, lineup1, lineup2, pitcher1, pitcher2):
        team1Score = 0
        team2Score = 0
        next_lineup1_list = [0]
        next_lineup2_list = [0]
        results = []

        for i in range(9):
                next_in_line1 = next_lineup1_list[-1]
                runs, new_lineup_index, half_inning_sequence  = half_inning(lineup1, next_in_line1, pitcher2, visualize = self.vis)
                next_lineup1_list.append(new_lineup_index)
                results.append(half_inning_sequence)
                team1Score += runs

                next_in_line2 = next_lineup2_list[-1]
                runs, new_lineup_index, half_inning_sequence = half_inning(lineup2, next_in_line2, pitcher1, visualize = self.vis)
                next_lineup2_list.append(new_lineup_index)
                results.append(half_inning_sequence)
                team2Score += runs
        innings = 9
            # extra innnings
        if team1Score == team2Score:
                self.extra_inning_games += 1
                while team1Score == team2Score:

                    runs1, new_lineup_index, half_inning_sequence1 = half_inning(lineup1, next_in_line1, pitcher2, visualize = self.vis)
                    next_lineup1_list.append(new_lineup_index)
                    team1Score += runs1

                    runs2, new_lineup_index, half_inning_sequence2 = half_inning(lineup2, next_in_line2, pitcher1, visualize = self.vis)
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
        if self.vis == 'y':
            plt.title(f'{team1.name} ({team1.color}) vs. {team2.name} ({team2.color})')
            plt.xlabel('Games')
            plt.ylabel('Wins')
            plt.show()
