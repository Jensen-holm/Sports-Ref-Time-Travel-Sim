import pandas as pd

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
        self.TB = self.singles + (self.doubles * 2) + (self.triples * 3) + (self.HR * 4)
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
            self.TB = self.singles + (self.doubles * 2) + (self.triples * 3) + (self.HR * 4)
            self.SLG = self.TB / self.AB
            self.OPS = self.OBP + self.SLG
            self.BA = self.H / self.AB
            self.OPS = self.OBP + self.SLG
            self.RC = ((self.H + self.BB) * self.TB) / self.BB + self.AB
            print(f'{self.Name} PA: {self.PA} AVG: {self.BA:.3f} HR: {self.HR} OBP: {self.OBP:.3f} OPS: {self.OPS:.3f} RBI: {self.RBI} HBP: {self.HBP}')
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
            else:
                self.weird = True

            if self.df.at[0, 'BB'] > 0:
                self.BBp = self.df.at[0, 'BB'] / self.df.at[0, 'BF']
            elif self.df.at[0, 'BB'] == 0:
                self.BBp = 0
            else:
                self.weird = True

            if self.df.at[0, 'HBP'] > 0:
                self.HBPp = self.df.at[0, 'HBP'] / self.df.at[0, 'BF']
            elif self.df.at[0, 'HBP'] == 0:
                self.HBPp = 0
            else:
                self.weird = True

            if self.df.at[0, 'H'] > 0:
                self.Hp = self.df.at[0, 'H'] / self.df.at[0, 'BF']
            elif self.df.at[0, 'H'] == 0:
                self.Hp = 0
            else:
                self.weird = True

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

    def __init__(self, hit_df, pit_df, scrap, team_name, color, line_settings):
        # for graphs
        self.color = color
        self.hit_prob = hit_df
        self.pit_prob = pit_df
        self.scrap = scrap
        self.name = team_name
        self.hitters, self.pitchers = self.generate_players()
        self.lineup_settings = line_settings

        self.batting_roster = [hitter for hitter in self.hitters if hitter.weird == False]

        if self.lineup_settings == 'manual':
            # hitters
            for player in self.hitters:
                if player.weird == False:
                    print(player.Name)
            print('\n -- SET LINEUP --\n(must enter 9)')
            lineup_names = []
            for i in range(9):
                lineup_names.append(input(str(i + 1) + ': '))
            print('\n')
            # now pitchers
            for player in self.pitchers:
                if player.weird == False:
                    print(player.Name)
            print('\n -- SET PITCHERS --\n(enter . to quit adding pitchers)')
            rotation_names = ['']
            i = 1
            while rotation_names[-1] != '.':
                rotation_names.append(input(str(i) + ': '))
                i += 1
            print('\n')

            self.lineup =[]
            for name in lineup_names:
                for player in self.hitters:
                    if name == player.Name:
                        self.lineup.append(player)
            self.rotation = []
            for name in rotation_names:
                for player in self.pitchers:
                    if name == player.Name:
                        self.rotation.append(player)
    
        elif self.lineup_settings == 'auto':
            self.lineup = [hitter for hitter in self.hitters if hitter.weird == False] #and 'P' not in hitter.df.at['Pos'] and 'CL' not in hitter.df.at[0, 'Pos']]
            self.lineup.sort(key = lambda x: x.df.at[0, 'TB'], reverse = True)
            self.lineup = self.lineup[:9]
            # rn the rotation is starters only for auto settings
            if self.scrap.level.lower() == 'mlb':
                self.rotation = [pitcher for pitcher in self.pitchers if pitcher.weird == False and pitcher.df.at[0, 'Pos'] == 'SP' or pitcher.df.at[0, 'Pos'] == 'P'] # excluding pure relievers (doesnt work on other leagues)
            elif self.scrap.level.lower() == 'other':
                self.rotation = [pitcher for pitcher in self.pitchers] # mess with it later
                self.rotation.sort(key = lambda x: x.df.at[0, 'IP'], reverse = True)
                self.rotation = self.rotation[:10] # 10 pitchers?

        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.games = self.draws + self.wins + self.losses 

    def generate_players(self):
        hit_names = self.hit_prob['Name'].unique()
        hit_names = [name for name in hit_names if name != 'None' and 'totals' not in name.lower() and 'Rank' not in name and 'Player' not in name]
        pit_names = self.pit_prob['Name'].unique()        
        pit_names = [name for name in pit_names if name != 'None' and 'totals' not in name.lower() and 'Rank' not in name and 'Player' not in name]
        hitters = [Player(self.hit_prob[self.hit_prob['Name'] == name], self.scrap, hitter = True, team_name = self.name) for name in hit_names]
        pitchers = [Player(self.pit_prob[self.pit_prob['Name'] == name], self.scrap, hitter = False, team_name = self.name) for name in pit_names]
        return hitters, pitchers
