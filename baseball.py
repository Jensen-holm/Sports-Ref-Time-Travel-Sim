from nwl_scrape import ScrapeNWL, nwl_id_dict
from NWL_functions import half_inningOther
from features import OptLineup, Situation
from objects import Team
from statistics import mode, median

class Baseball():

    level = 'nwl'

    def __init__(self):
        # print out team options
        for key in nwl_id_dict.keys():
            print(key)
        self.team1_name = input('\nEnter Team 1 (ex: Growlers): ').title().strip()
        self.team2_name = input('Enter Team 2 (ex: Kingfish): ').title().strip()
        # else:
        #     print('\nMUST ENTER MLB, OR NWL (other leagues currently not supported)')


        # prompt about lineup optimizer
        self.lineup_optimizer = input('\nAre you here for the lineup optimizer? (y/n): ').strip().lower()

        if self.lineup_optimizer == 'y':
            # prompt to select which bullpen pitchers the other team will use as well once we get that incorperated
                data1 = ScrapeNWL(self.team1_name)
                data2 = ScrapeNWL(self.team2_name)
                team1 = Team(self.level, 'opt', self.team1_name, data1[0][0], data1[0][1], data1[0][2], data1[0][3])
                team2 = Team(self.level, 'opt', self.team2_name, data2[0][0], data2[0][1], data2[0][2], data2[0][3])
                print('\n')
                # prompt user to pick starting pitcher to sim against
                for pitcher in team2.pitchers:
                    print(f'{pitcher.Name} {pitcher.hand}')
                pitcher_name = input('\nWHICH PITCHER ARE WE FACING?: ').title().strip()
                pitcher = [pitcher for pitcher in team2.pitchers if pitcher_name == pitcher.Name][0]
                OptLineup(team1.hitters, pitcher, half_inningOther)

        else:
            # situational option
            self.situational = input('\nAre you here for Situational Analysis? (y/n): ').strip().lower()
            if self.situational == 'y':

                team1 = Team(self.level, 'manual', self.team1_name)
                team2 = Team(self.level, 'manual', self.team2_name)
                Situation(team1, team2, half_inningOther)

            else:
                self.lineup_settings = input('\nLineup Settings (manual/auto): ').strip().lower()
                data1 = ScrapeNWL(self.team1_name)
                data2 = ScrapeNWL(self.team2_name)

                team1 = Team(self.level, self.lineup_settings, self.team1_name, data1[0][0], data1[0][1], data1[0][2], data1[0][3])
                team2 = Team(self.level, self.lineup_settings, self.team2_name, data2[0][0], data2[0][1], data2[0][2], data2[0][3])

                self.num_sims = int(input('\nENTER NUMBER OF SIMULATIONS: '))

                # keep track of numbers
                self.game_scores = []
                self.other_stats = []
                self.extra_inning_games = 0

                if self.level == 'nwl':
                    self.simulation(team1, team2, self.Othergame)
                elif self.level == 'mlb':
                    # self.simulation(team1, team2, self.MLBgame)
                    print(f'\nCURRENTLY ONLY THE NORTHWOODS LEAGUE IS SUPPORTED WITH SPLIT STATISTICS.\n')
                else: # generic simulation with no split stats
                    print(f'\n{self.level.title()} IS NOT CURRENTLY SUPPORTED.\n')

                self.Summary(team1, team2)



    def Othergame(self, team1, team2, lineup1, lineup2, pitcher1, pitcher2):

        team1Score = 0
        team2Score = 0
        next_lineup1_list = [0]
        next_lineup2_list = [0]
        results = []

        for i in range(9):
                next_in_line1 = next_lineup1_list[-1]
                runs, new_lineup_index, half_inning_sequence  = half_inningOther(lineup1, next_in_line1, pitcher2)
                next_lineup1_list.append(new_lineup_index)
                results.append(half_inning_sequence)
                team1Score += runs

                next_in_line2 = next_lineup2_list[-1]
                runs, new_lineup_index, half_inning_sequence = half_inningOther(lineup2, next_in_line2, pitcher1)
                next_lineup2_list.append(new_lineup_index)
                results.append(half_inning_sequence)
                team2Score += runs
        innings = 9

        # extra innnings
        if team1Score == team2Score:
                self.extra_inning_games += 1
                while team1Score == team2Score:

                    runs1, new_lineup_index, half_inning_sequence1 = half_inningOther(lineup1, next_in_line1, pitcher2)
                    next_lineup1_list.append(new_lineup_index)
                    team1Score += runs1

                    runs2, new_lineup_index, half_inning_sequence2 = half_inningOther(lineup2, next_in_line2, pitcher1)
                    next_lineup2_list.append(new_lineup_index)
                    team2Score += runs2

                    results.append([[half_inning_sequence1], [half_inning_sequence2]])
                    innings += 1

        # determine winner
        if team1Score > team2Score:
            team1.wins += 1
            team2.losses += 1
            print(f'\nTHE {team1.team_name} WIN!')
            print(f'SCORE: {team1Score} to {team2Score}\n')
        elif team1Score < team2Score:
            print(f'\nTHE {team2.team_name} WIN!')
            print(f'SCORE: {team1Score} to {team2Score}\n')
            team1.losses += 1
            team2.wins += 1
            # find the longest game, and most probable scores for each team using this info below
        self.game_scores.append([team1Score, team2Score, innings])
        self.other_stats.append(results)

    def MLBgame(self):

        return

    # game function is either mlbGame or other game (rn only othergame is done)
    def simulation(self, team1, team2, game_func): # game func should be either the MLB game or other game functions

            # cycle through bullpens as well eventually
                games = 0
                pitcher_index1 = 0
                pitcher_index2 = 0
                for i in range(self.num_sims // 2):
                    game_func(team1, team2, team1.lineup, team2.lineup, team1.rotation[pitcher_index1], team2.rotation[pitcher_index2])
                    pitcher_index1 += 1
                    pitcher_index2 += 1
                    games += 1

                    if pitcher_index1 == len(team1.rotation):
                        pitcher_index1 = 0
                    if pitcher_index2 == len(team2.rotation):
                        pitcher_index2 = 0

                pitcher_index1 = 0
                pitcher_index2 = 0
                for i in range(self.num_sims // 2):
                    game_func(team2, team1, team2.lineup, team1.lineup, team2.rotation[pitcher_index2], team1.rotation[pitcher_index1])
                    pitcher_index1 += 1
                    pitcher_index2 += 1
                    games += 1

                    if pitcher_index1 == len(team1.rotation):
                        pitcher_index1 = 0
                    if pitcher_index2 == len(team2.rotation):
                        pitcher_index2 = 0


    def Summary(self, team1, team2):
        print('\n\n- - - - - - - - - - RESULTS - - - - - - - - - -\n\n')

        print(f'\n-- {team1.team_name} lineup statistics --\n')
        for player in team1.lineup:
            player.rate_stats()

        print(f'\n-- {team1.team_name} rotation statistics --\n')
        for pitcher in team1.rotation:
            pitcher.rate_stats()

        print(f'\n-- {team2.team_name} lineup statistics --\n')
        for player in team2.lineup:
            player.rate_stats()

        print(f'\n-- {team2.team_name} rotation statistics --\n')
        for pitcher in team2.pitchers:
            pitcher.rate_stats()

        print('\n - - - WIN PROBABILITY - - -\n')

        print(f'{team1.team_name} record: {team1.wins} - {team1.losses}')
        print(f'{team2.team_name} record: {team2.wins} - {team2.losses}')

        print(f'\n{team1.team_name}: {(team1.wins / (team1.losses + team1.wins)) * 100:.2f}%')
        print(f'{team2.team_name}: {(team2.wins / (team2.losses + team2.wins)) * 100:.2f}%')

        mode1 = mode([x[0] for x in self.game_scores])
        mode2 = mode([x[1] for x in self.game_scores])
        print(f'\nRuns per game for the {team1.team_name}: {sum([x[0] for x in self.game_scores]) / (team1.wins + team1.losses):.2f}')
        print(f'Runs per game for the {team2.team_name}: {sum([x[1] for x in self.game_scores]) / (team2.wins + team2.losses):.2f}')
        print(f'\nMedian Score for the {team1.team_name}: {median([x[0] for x in self.game_scores])} ')
        print(f'Median Score for the {team2.team_name}: {median([x[1] for x in self.game_scores])}')
        print(f'\nMost common score for the {team1.team_name}: {mode([x[0] for x in self.game_scores])} ({([x[0] for x in self.game_scores].count(mode1) / len(self.game_scores)) * 100:.2f}%)')
        print(f'Most common score for the {team2.team_name}: {mode([x[1] for x in self.game_scores])} ({([x[1] for x in self.game_scores].count(mode2)) / len(self.game_scores) * 100:.2f}%)')
        print(f'\nProbability of the {team1.team_name} shutting out the {team2.team_name}: {([x[1] for x in self.game_scores].count(0) / len(self.game_scores)) * 100:.2f}%')
        print(f'Probability of the {team2.team_name} shutting out the {team1.team_name}: {([x[0] for x in self.game_scores].count(0) / len(self.game_scores)) * 100:.2f}%')
        print(f'\nLongest game (currently no extra innings rule): {max([x[2] for x in self.game_scores])} innings\n')
