from scrape import ScrapeSR
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import random

class Player():

    def __init__(self, df_row, scrap, hitter, team_name):
        self.hitter = hitter
        self.weird = False
        self.team = team_name

        if self.hitter == True:
            self.df = pd.DataFrame(df_row, columns = scrap.hit_cols)
            self.df.reset_index(inplace = True)
            self.df = self.df.apply(pd.to_numeric, errors = 'coerce').combine_first(self.df)
            self.Name = self.df.at[0, 'Name']
            self.hitter_probs()

        elif self.hitter == False:
            self.df = pd.DataFrame(df_row, columns = scrap.pit_cols)
            self.df.reset_index(inplace = True)
            self.df = self.df.apply(pd.to_numeric, errors = 'coerce').combine_first(self.df)
            self.Name = self.df.at[0, 'Name']
            self.pitcher_probs()

        self.K = 0
        self.BB = 0
        self.H = 0
        self.HBP = 0
        self.singles = 0
        self.doubles = 0
        self.triples = 0
        self.HR = 0
        self.IPO = 0
        self.AB = 0
        self.PA = 0
        self.RBI = 0
        # stats unique to pitchers
        if self.hitter == False:
            self.IP = 0
            self.BF = 0
            self.ER = 0

    ''' ----------------------------- Probability and stat functions --------------------------------- '''
    # call the rate stats funciton when the simulations are over
    def rate_stats(self):
        if self.hitter == True:
            self.OBP = (self.BB + self.HBP + self.H) / self.PA
            self.SLG = (self.singles + (self.doubles * 2) + (self.triples * 3) + (self.HR * 4)) / self.AB
            self.OPS = self.OBP + self.SLG
            self.BA = self.H / self.AB
            print(f'{self.Name} PA: {self.PA}, RBI: {self.RBI}, HR: {self.HR}, AVG: {self.BA:.3f}, OBP: {self.OBP:.3f}, SLG%: {self.SLG:.3f}, BB: {self.BB}, K: {self.K}')
        elif self.hitter == False:
            # not alot of these are actually incremented yet
            self.WHIP = (self.BB + self.H) / self.IP
            self.ERA = (9 * self.ER) / self.IP
            self.HR_9 = self.HR / (self.IP / 9)
            self.K_9 = self.K / (self.IP / 9)
            self.BB_9 = self.BB / (self.IP / 9)
            self.K_BB = self.K / self.BB
            print(f'{self.Name} IP: {self.IP}, ERA: {self.ERA:.2f}, WHIP: {self.WHIP:.3f}, K/9: {self.K_9:.2f}, K/BB: {self.K_BB:.2f}')

    def pitcher_probs(self):
        if self.df.at[0, 'BF'] > 0:

            if self.df.at[0, 'SO'] > 0:
                self.Kp = self.df.at[0, 'SO'] / self.df.at[0, 'BF']
            elif self.df.at[0, 'SO'] == 0:
                self.Kp = 0

            if self.df.at[0, 'BB'] > 0:
                self.BBp = self.df.at[0, 'BB'] / self.df.at[0, 'BF']
            elif self.df.at[0, 'BB'] == 0:
                self.BBp = 0

            if self.df.at[0, 'HBP'] > 0:
                self.HBPp = self.df.at[0, 'HBP'] / self.df.at[0, 'BF']
            elif self.df.at[0, 'HBP'] == 0:
                self.HBPp = 0

            if self.df.at[0, 'H'] > 0:
                self.Hp = self.df.at[0, 'H'] / self.df.at[0, 'BF']
            elif self.df.at[0, 'H'] == 0:
                self.Hp = 0

            self.IPOp = 1 - (self.Hp + self.HBPp + self.BBp + self.Kp)

        else:
            self.weird = True



    def hitter_probs(self):
        if self.df.at[0, 'H'] > 0 and self.df.at[0, 'PA'] > 0:
            self.df['1B'] = self.df['H'] - (self.df['2B'] + self.df['3B'] + self.df['HR'])
            self.Kp = self.df.at[0, 'SO'] / self.df.at[0, 'PA']
            self.BBp = self.df.at[0, 'BB'] / self.df.at[0, 'PA']
            self.HBPp = self.df.at[0, 'HBP'] / self.df.at[0, 'PA']
            self.Hp = self.df.at[0, 'H'] / self.df.at[0, 'PA']
            self.IPOp = 1 - (self.Hp + self.BBp + self.HBPp + self.Kp)

            # total base probabilities if hit is the outcome
            if self.df.at[0, '1B']  > 0:
                self.singlep = self.df.at[0, '1B'] / self.df.at[0, 'H']
            elif self.df.at[0, '1B'] == 0:
                self.singlep = 0

            if self.df.at[0, '2B'] > 0:
                self.doublep = self.df.at[0, '2B'] / self.df.at[0, 'H']
            elif self.df.at[0, '2B'] == 0 :
                self.doublep = 0

            if self.df.at[0, '3B'] > 0:
                self.triplep = self.df.at[0, '3B'] / self.df.at[0, 'H']
            elif self.df.at[0, '3B'] == 0:
                self.triplep = 0

            if self.df.at[0, 'HR'] > 0:
                self.HRp = self.df.at[0, 'HR'] / self.df.at[0, 'H']
            elif self.df.at[0, 'HR'] == 0:
                self.HRp = 0

        else:
            self.weird = True


class Team():

    def __init__(self, hit_df, pit_df, scrap, team_name):
        self.hit_prob = hit_df
        self.pit_prob = pit_df
        self.scrap = scrap
        self.name = team_name
        self.hitters, self.pitchers = self.generate_players()
        self.lineup = [hitter for hitter in self.hitters if hitter.weird == False]
        self.rotation = [pitcher for pitcher in self.pitchers if pitcher.weird == False]

        self.wins = 0
        self.losses = 0
        self.draws = 0

    def generate_players(self):
        hit_names = self.hit_prob['Name'].unique()
        hit_names = [name for name in hit_names if name != 'None' and 'totals' not in name.lower() and 'Rank' not in name]
        pit_names = self.pit_prob['Name'].unique()
        pit_names = [name for name in pit_names if name != 'None' and 'totals' not in name.lower() and 'Rank' not in name]

        hitters = [Player(self.hit_prob[self.hit_prob['Name'] == name], self.scrap, hitter = True, team_name = self.name) for name in hit_names]
        pitchers = [Player(self.pit_prob[self.pit_prob['Name'] == name], self.scrap, hitter = False, team_name = self.name) for name in pit_names]
        return hitters, pitchers


class Baseball():

    def __init__(self):

        self.LEVEL = input('\nENTER LEVEL OF COMPETITION (mlb or other): ').title().strip()

        if self.LEVEL.lower() == 'other':
            self.league = input('\nENTER LEAGUE NAME: ').title().strip()

        self.TEAM1 = input('\nENTER TEAM 1 (ex: 1899 Cincinnati Reds): ').title().strip()
        self.TEAM2 = input('ENTER TEAM 2 (ex: 1927 New York Yankees): ').title().strip()

        if self.LEVEL.lower() == 'other':
            scraper = ScrapeSR('Baseball', self.league, self.TEAM1, self.TEAM2, self.LEVEL)
            
        elif self.LEVEL.lower() == 'mlb':
            scraper = ScrapeSR('Baseball', 'mlb', self.TEAM1, self.TEAM2, self.LEVEL)

        self.team1hit = scraper.hit1
        self.team2hit = scraper.hit2
        self.team1pit = scraper.pit1
        self.team2pit = scraper.pit2

        Team1 = Team(self.team1hit, self.team1pit, scraper, self.TEAM1)
        Team2 = Team(self.team2hit, self.team2pit, scraper, self.TEAM2)

        self.num_sims = int(input('\nENTER NUMBER OF SIMULATIONS: '))

        # so they play equal home / road games

        t1i = 0
        t2i = 0
        ''' fix the pitching situation '''
        for i in range(self.num_sims // 2):
                if t1i == len(Team1.rotation):
                    t1i = 0
                if t2i == len(Team2.rotation):
                    t2i = 0
                self.game(Team1, Team2, Team1.lineup, Team2.lineup, Team1.rotation[t1i], Team2.rotation[t2i])
                t1i += 1
                t2i += 1
                
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

        # summary
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
            print(f'{hitter.Name} hits a {1 + len(bases_occupied)} run BOMB off of {pitcher.Name}')
            base_state = self.clear_bases(base_state)

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
                        print(f'{base_state[2].Name} scores after {hitter.Name} {play_result}')
                        runs_scored_on_play += 1
                        base_state[2] = None
                        base_state[1] = base_state[0]
                        base_state[0] = hitter
                    elif play_result == '2B':
                        print(f'{base_state[2].Name} and {base_state[0].Name} scores after {hitter.Name} {play_result}')
                        runs_scored_on_play += 2
                        base_state[1] = hitter
                        base_state[0] = None
                        base_state[2] = None

            # bases loaded (3 runners on)
            elif len(bases_occupied) == 3:
                if play_result == 'BB' or play_result == 'HBP':
                    print(f'{base_state[2].Name} scores after {hitter.Name} {play_result}')
                    runs_scored_on_play += 1
                    base_state[2] = base_state[1]
                    base_state[1] = base_state[0]
                    base_state[0] = hitter
                elif play_result == '1B':
                    print(f'{base_state[2].Name} scores after {hitter.Name} {play_result}')
                    runs_scored_on_play += 1
                    base_state[2] = base_state[1]
                    base_state[1] = base_state[0]
                    base_state[0] = hitter
                elif play_result == '2B':
                    runs_scored_on_play += 2
                    print(f'{base_state[2].Name} and {base_state[1].Name} scores after {hitter.Name} {play_result}')
                    base_state[2] = base_state[0]
                    base_state[1] = hitter
                    base_state[0] = None
        hitter.RBI += runs_scored_on_play
        pitcher.ER += runs_scored_on_play
        return base_state, runs_scored_on_play



    def half_inning(self, lineup, current_batsman_index, pitcher, hitting_team_score):
        # maybe we sort lineups by stats using lambda eventually
        hitting_team_score = hitting_team_score
        base_state = [None,None,None]
        outs = 0
        index = current_batsman_index

        if current_batsman_index >= len(lineup):
            index = 0

        while outs < 3:

            result = self.PA(lineup[index], pitcher)            
            print(f'{lineup[index].team} {lineup[index].Name} {result}')

            # check if there was an out
            if result == 'IPO':
                lineup[index].IPO += 1
                index += 1
                outs += 1
            elif result == 'K':
                lineup[index].K += 1
                pitcher.K += 1
                index += 1
                outs += 1

            # then if it was something else
            elif result == 'HBP':
                base_state, scored = self.advance_bases(base_state, result, lineup[index], pitcher)
                hitting_team_score += scored
                pitcher.HBP += 1
                lineup[index].HBP += 1
                index += 1
            elif result == 'BB':
                base_state, scored = self.advance_bases(base_state, result, lineup[index], pitcher)
                hitting_team_score += scored
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
                    hitting_team_score += scored
                    lineup[index].singles += 1
                    pitcher.singles += 1
                    index += 1
                elif hit_type == '2B':
                    base_state, scored = self.advance_bases(base_state, hit_type, lineup[index], pitcher)
                    hitting_team_score += scored
                    lineup[index].doubles += 1
                    pitcher.doubles += 1
                    index += 1
                elif hit_type == '3B':
                    base_state, scored = self.advance_bases(base_state, hit_type, lineup[index], pitcher)
                    hitting_team_score += scored
                    lineup[index].triples += 1
                    pitcher.triples += 1
                    index += 1
                elif hit_type == 'HR':
                    base_state, scored = self.advance_bases(base_state, hit_type, lineup[index], pitcher)
                    hitting_team_score += scored
                    lineup[index].HR += 1
                    pitcher.HR += 1
                    index += 1
            if index == len(lineup):
                index = 0
        pitcher.IP += 1
        return hitting_team_score, index

    def game(self, team1, team2, lineup1, lineup2, pitcher1, pitcher2):
        # maybe we prompt the user to set lineups after printing all available hitters to choose from
        # pitchers as well
        lineup1 = lineup1[:9]
        lineup2 = lineup2[:9]
        team1Score = 0
        team2Score = 0
        next_lineup1_list = [0]
        next_lineup2_list = [0]
        next_in_line1 = next_lineup1_list[-1]
        next_in_line2 = next_lineup2_list[-1]
        for i in range(9):
            runs, new_lineup_index  = self.half_inning(lineup1, next_in_line1, pitcher2, team1Score)
            next_lineup1_list.append(new_lineup_index)
            team1Score += runs

            runs, new_lineup_index = self.half_inning(lineup2, next_in_line2, pitcher1, team2Score)
            next_lineup2_list.append(new_lineup_index)
            team2Score += runs

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
            print(f'\nAnd this one belongs to the {team1.name}')
            team2.losses += 1
        elif team1Score < team2Score:
            print(f'\nAnd this one belongs to the {team2.name}')
            team1.losses += 1
            team2.wins += 1
        # while we still do not have extra innings done yet
        elif team1Score == team2Score:
            print(f'\nTIE (working on extra innings)')
            team1.draws += 1
            team2.draws += 1

        print(f'\n{team1.name} wins, losses, ties: {team1.wins} {team1.losses} {team1.draws}')
        print(f'{team2.name} wins, losses, ties: {team2.wins} {team2.losses} {team2.draws}\n\n')

    ''' -------------------------- Summary Functions -----------------------------'''

    # def sum_hitter(self, hitter):
    #     print(f'\n{hitter.Name} Hits: {hitter.H}')

    # def sum_pitcher(self, pitcher):
    #     print(f'\n{pitcher.Name} Strikeouts: {pitcher.K}')

    def sum_team(self, team):
        print('')

    def summary(self, team1, team2):
        for i in range(9):
            print('-', end = ' ')
        print('RESULTS', end = ' ')
        for i in range(10):
            print('-', end = ' ')
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
        print('\n\nWINNING PERCENTAGE')
        print(f'In {team1.wins + team1.losses + team1.draws} simulated games...')
        print(f'\n{team1.name}: {(team1.wins / (team1.wins + team1.losses + team1.draws)) * 100:.2f}%')
        print(f'{team2.name}: {(team2.wins / (team2.wins + team2.losses + team2.draws)) * 100:.2f}%\n')
