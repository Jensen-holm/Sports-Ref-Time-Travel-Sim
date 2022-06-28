import math
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=RuntimeWarning)

class NWLHitter():
    def __init__(self, df_row_l, df_row_r, team_name):
        self.weird_l = False
        self.weird_r = False
        self.df_l = pd.DataFrame(df_row_l).apply(pd.to_numeric, errors = 'ignore').fillna(0)
        self.df_r = pd.DataFrame(df_row_r).apply(pd.to_numeric, errors = 'ignore').fillna(0)
        self.df_l.reset_index(inplace = True)
        self.df_r.reset_index(inplace = True)
        self.Name = self.df_l.at[0, 'PLAYER']
        self.team_name = team_name

        if self.df_l.at[0, 'HAND'] == '*':
            self.hand = 'L'
        elif self.df_l.at[0, 'HAND'] == '#':
            self.hand = 'S'
        else:
            self.hand = 'R'

        if self.df_l.at[0, 'STATUS'] == 'X':
            self.status = self.df_l.at[0, 'STATUS']
        else:
            self.status = '*'

        self.df_l['1B'] = self.df_l['H'] - (self.df_l['2B'] + self.df_l['3B'] + self.df_l['HR'])
        self.df_r['1B'] = self.df_r['H'] - (self.df_r['2B'] + self.df_r['3B'] + self.df_r['HR'])
        self.df_r['ATT'] = self.df_r['SB'] + self.df_r['CS']
        self.df_l['ATT'] = self.df_l['SB'] + self.df_l['CS']

        self.probsL, self.probsR = self.probability()

        for prob in self.probsL:
            if math.isnan(prob[1]) == True:
                prob[1] = 0
        for prob in self.probsR:
            if math.isnan(prob[1]) == True:
                prob[1] = 0

        # keep track of stats
        self.PA = 0
        self.AB = 0
        self.ROE = 0
        self.H = 0
        self.HBP = 0
        self.singles = 0
        self.doubles = 0
        self.triples = 0
        self.HR = 0
        self.RBI =  0
        self.SB = 0
        self.CS = 0
        self.ATT = self.SB + self.CS
        self.DP = 0
        self.SF = 0
        self.SH = 0
        self.PK = 0
        self.IPO = 0
        self.K = 0
        self.BB = 0


    def probability(self):

        numeric_columns = self.df_r.select_dtypes(include = ['float', 'int'])
        probsL = []
        probsR = []

        # in play out left and right (make sure this is correct...)
        IPOpr  = 1 - ((self.df_r.at[0, 'ROE'] / self.df_r.at[0, 'PA']) + (self.df_r.at[0, 'H'] / self.df_r.at[0, 'PA']) + (self.df_r.at[0, 'BB'] / self.df_r.at[0, 'PA']) + (self.df_r.at[0, 'HBP'] / self.df_r.at[0, 'PA']))
        IPOpl = 1 - ((self.df_l.at[0, 'ROE'] / self.df_l.at[0, 'PA']) + (self.df_l.at[0, 'H'] / self.df_l.at[0, 'PA']) + (self.df_l.at[0, 'BB'] / self.df_l.at[0, 'PA']) + (self.df_l.at[0, 'HBP'] / self.df_l.at[0, 'PA']))

        probsR.append(['IPO', IPOpr])
        probsL.append(['IPO', IPOpl])

        for col in numeric_columns:
            if self.df_l.at[0, 'PA'] > 0:
                if col not in ['1B', '2B', '3B', 'HR', 'SB', 'CS', 'PK']:# check if its a hit column, so we would have to divive by H not PA, and SB columns are different too
                    prob = self.df_l.at[0, col] / self.df_l.at[0, 'PA']
                    probsL.append([col, prob])
                elif col in ['1B', '2B', '3B', 'HR']:
                    prob = self.df_l.at[0, col] / self.df_l.at[0, 'H']
                    probsL.append([col, prob])
                elif col == 'PK':
                    prob = self.df_l.at[0, 'PK'] / (self.df_l.at[0, '1B'] + self.df_l.at[0, 'BB'] + self.df_l.at[0, 'HBP'])
                    probsL.append([col, prob])
                elif col in ['SB', 'CS']:
                    prob = self.df_l.at[0, col] / self.df_l.at[0, 'ATT']
                    probsL.append([col, prob])
            else:
                self.weird_l = True

            # then do right handed
            if self.df_r.at[0, 'PA'] > 0:
                if col not in ['1B', '2B', '3B', 'HR', 'SB', 'CS', 'PK']:# check if its a hit column, so we would have to divive by H not PA, and SB columns are different too
                    prob = self.df_r.at[0, col] / self.df_r.at[0, 'PA']
                    probsR.append([col, prob])
                elif col in ['1B', '2B', '3B', 'HR']:
                    prob = self.df_r.at[0, col] / self.df_r.at[0, 'H']
                    probsR.append([col, prob])
                elif col == 'PK':
                    prob = self.df_r.at[0, 'PK'] / (self.df_r.at[0, '1B'] + self.df_r.at[0, 'BB'] + self.df_r.at[0, 'HBP'])
                    probsR.append([col, prob])
                elif col in ['SB', 'CS']:
                    prob = self.df_r.at[0, col] / self.df_r.at[0, 'ATT']
                    probsR.append([col, prob])
            else:
                self.weird_r = True
        return probsL, probsR


    def rate_stats(self):
            self.AVG = self.H / self.AB
            self.OBP = (self.H + self.BB + self.HBP) / self.PA
            self.SLG = (self.singles + (self.doubles * 2) + (self.triples * 3) + (self.HR * 4)) / self.AB
            self.OPS = self.OBP + self.SLG
            print(f'{self.Name} {self.hand}: PA: {self.PA} AVG: {self.AVG:.3f} OBP: {self.OBP:.3f} SLG: {self.SLG:.3f} OPS: {self.OPS:.3f} HR: {self.HR} RBI: {self.RBI}')

''' pitchers dataframes are empty right now for some teams '''
class NWLPitcher():
    def __init__(self, df_row_l, df_row_r, team_name):
        self.weird_l = False
        self.weird_r = False
        self.df_l = pd.DataFrame(df_row_l).apply(pd.to_numeric, errors = 'ignore')
        self.df_r = pd.DataFrame(df_row_r).apply(pd.to_numeric, errors = 'ignore')
        self.df_l.reset_index(inplace = True)
        self.df_r.reset_index(inplace = True)

        if self.df_l.at[0, 'HAND'] == '*':
            self.hand = 'L'
        elif self.df_l.at[0, 'HAND'] == '#':
            self.hand = 'S'
        else:
            self.hand = 'R'

        if self.df_l.at[0, 'STATUS'] == 'X':
            self.status = self.df_r.at[0, 'STATUS']
        else:
            self.status = '*'

        if len(self.df_l) > 0 and len(self.df_r) > 0:
            self.Name = self.df_l.at[0, 'PLAYER']
            self.df_l['1B'] = self.df_l['H'] - (self.df_l['2B'] + self.df_l['3B'] + self.df_l['HR'])
            self.df_r['1B'] = self.df_r['H'] - (self.df_r['2B'] + self.df_r['3B'] + self.df_r['HR'])

            self.probsL, self.probsR = self.probability()

            for prob in self.probsL:
                if math.isnan(prob[1]) == True:
                    prob[1] = 0
            for prob in self.probsR:
                if math.isnan(prob[1]) == True:
                    prob[1] = 0

        else:
            self.weird_l = True
            self.weird_r = True
            self.Name = 'N/A'        

        self.IP = 0
        self.BF = 0
        self.K = 0
        self.H = 0
        self.BB = 0
        self.HBP = 0
        self.IPO = 0
        self.ER = 0
        self.R = 0
        self.UER = 0
        self.PK = 0
        self.BK = 0
        self.IPO = 0
        self.ROE = 0
        self.singles = 0
        self.doubles = 0
        self.triples = 0
        self.HR = 0

    def probability(self):
        numeric_columns = self.df_r.select_dtypes(include = ['float', 'int'])
        probsL = []
        probsR = []
        # in play out left and right (make sure this is correct...)
        # no reach on error probability for pitcher which I think is fine
        IPOpr  = 1 - ((self.df_r.at[0, 'H'] / self.df_r.at[0, 'BF']) + (self.df_r.at[0, 'BB'] / self.df_r.at[0, 'BF']) + (self.df_r.at[0, 'HB'] / self.df_r.at[0, 'BF']))
        IPOpl = 1 - ((self.df_l.at[0, 'H'] / self.df_l.at[0, 'BF']) + (self.df_l.at[0, 'BB'] / self.df_l.at[0, 'BF']) + (self.df_l.at[0, 'HB'] / self.df_l.at[0, 'BF']))
        probsR.append(['IPO', IPOpr])
        probsL.append(['IPO', IPOpl])
        for col in numeric_columns:
            if self.df_l.at[0, 'BF'] > 0:
                if col not in ['1B', '2B', '3B', 'HR', 'SB', 'CS', 'PK']:# check if its a hit column, so we would have to divive by H not PA, and SB columns are different too
                    prob = self.df_l.at[0, col] / self.df_l.at[0, 'BF']
                    probsL.append([col, prob])
                elif col in ['1B', '2B', '3B', 'HR']:
                    prob = self.df_l.at[0, col] / self.df_l.at[0, 'H']
                    probsL.append([col, prob])
                elif col == 'PK':
                    prob = self.df_l.at[0, 'PK'] / (self.df_l.at[0, '1B'] + self.df_l.at[0, 'BB'] + self.df_l.at[0, 'HB'])
                    probsL.append([col, prob])
            else:
                self.weird_l = True

            # then do right handed
            if self.df_r.at[0, 'BF'] > 0:
                if col not in ['1B', '2B', '3B', 'HR', 'SB', 'CS', 'PK']:# check if its a hit column, so we would have to divive by H not PA, and SB columns are different too
                    prob = self.df_r.at[0, col] / self.df_r.at[0, 'BF']
                    probsR.append([col, prob])
                elif col in ['1B', '2B', '3B', 'HR']:
                    prob = self.df_r.at[0, col] / self.df_r.at[0, 'H']
                    probsR.append([col, prob])
                elif col == 'PK':
                    prob = self.df_r.at[0, 'PK'] / (self.df_r.at[0, '1B'] + self.df_r.at[0, 'BB'] + self.df_r.at[0, 'HB'])
                    probsR.append([col, prob])
            else:
                self.weird_r = True
        return probsL, probsR

    # rate stats are messed for hitters and pitchers rn
    def rate_stats(self):
        if self.IP != 0:
            self.WHIP = (self.BB + self.H) / self.IP
            self.ERA = self.ER / (self.IP / 9) # not sure if this is it off the top of my head
            self.K_9 = self.K / (self.IP / 9)
            self.BB_9 = self.BB / (self.IP / 9)
            print(f'{self.Name} {self.hand}: WHIP: {self.WHIP:.2f} ERA: {self.ERA:.2f} K/9: {self.K_9:.2f}')

    # for the linuep optimizer
    def lineup_rate_stats(self):

        return


class Team():
    def __init__(self, level, lineup_settings, team_name, df_vrhp, df_vlhp, df_vrhh, df_vlhh):

        self.lineup_settings = lineup_settings
        self.team_name = team_name
        self.level = level
        self.vrhp = df_vrhp[df_vrhp['PLAYER'] != 'PLAYER']
        self.vlhp = df_vlhp[df_vlhp['PLAYER'] != 'PLAYER']
        self.vrhh = df_vrhh[df_vrhh['PLAYER'] != 'PLAYER']
        self.vlhh = df_vlhh[df_vlhh['PLAYER'] != 'PLAYER']

        self.hitters, self.pitchers = self.generate_players()

        self.lineup, self.rotation, self.bullpen = self.set_lineup()

        # stats
        self.wins = 0
        self.losses = 0

    def generate_players(self):
        # get names
        hit_namesr = self.vrhp['PLAYER'].unique()
        hit_namesl = self.vlhp['PLAYER'].unique()
        pit_namesr = self.vrhh['PLAYER'].unique()
        pit_namesl = self.vlhh['PLAYER'].unique()
        hitters = []
        pitchers = []
        if self.level != 'mlb':
            for namer in hit_namesr:
                for namel in hit_namesl:
                    if namer == namel:
                        rhp = self.vrhp[self.vrhp['PLAYER'] == namer]
                        lhp = self.vlhp[self.vlhp['PLAYER'] == namer]
                        hitters.append(NWLHitter(lhp, rhp, self.team_name))
            for namel in pit_namesl:
                for namer in pit_namesr:
                    if namel == namer:
                        rhh = self.vrhh[self.vrhh['PLAYER'] == namer]
                        lhh = self.vlhh[self.vlhh['PLAYER'] == namer]
                        pitchers.append(NWLPitcher(lhh, rhh, self.team_name))
        else:
            raise ValueError('MLB NOT CURRENTLY SUPPORTED WITH SPLIT STATS')
        return hitters, pitchers


    def set_lineup(self):
        if self.lineup_settings == 'manual':
            # prompt user to set the lineups if the didnt set it to auto
            print('\n')
            for player in self.hitters:
                print(str(player.Name) + ' ' + str(player.hand) + ' ' +  str(player.status))
            print(f'\nEnter the {self.team_name} Lineup (must enter 9 guys)')
            # take input
            hitter_names = []
            for i in range(9):
                i += 1
                hitter_names.append(input(str(i) + '. ').title().strip())
            print('\n')
            for player in self.pitchers:
                print(str(player.Name) + ' ' + str(player.hand) + ' ' + str(player.status))
            print('\nWho are the Starting Pitchers (press enter to stop)?')

            pitcher_names = [' ']
            i = 1
            while pitcher_names[-1] != '':
                pitcher_names.append(input(str(i) + '.  ').title().strip())
                i += 1
            # match entered names wiht names on the team roster
            # lineup
            lineup = []
            for name in hitter_names:
                for player in self.hitters:
                    if name == player.Name:
                        lineup.append(player)
            if len(lineup) != 9:
                raise ValueError('\nCHECK PLAYER NAME SPELLING. THERE NEED TO BE 9 PLAYERS IN THE LINEUP.\n')
            # same for pitchers
            rotation = []
            for name in pitcher_names:
                for player in self.pitchers:
                    if name == player.Name:
                        rotation.append(player)
            if len(rotation) != len(pitcher_names):
                raise ValueError('\nCHECK PITCHER SPELLING WHEN MANUALLY ENTERING LINEUPS.\n')
            # for now set the bullpen equal to everyone not in the lineup
            bullpen = [pitcher for pitcher in self.pitchers if pitcher not in rotation]
            return lineup, rotation, bullpen
        else: # default settings are auto lineups and rotations and bullpens
            self.pitchers = [pitcher for pitcher in self.pitchers if pitcher.weird_l == False and pitcher.weird_r == False and pitcher.status != 'X']
            self.hitters = [hitter for hitter in self.hitters if hitter.weird_l == False and hitter.weird_r == False and hitter.status != 'X']
            rotation = sorted(self.pitchers, key=lambda x: x.df_r.at[0, 'IP'] + x.df_l.at[0, 'IP'], reverse = True)[:6]
            bullpen = [pitcher for pitcher in self.pitchers if pitcher not in rotation] # everyone else goes in the pen
            lineup = sorted(self.hitters, key=lambda x: x.df_r.at[0, 'H'] + x.df_l.at[0, 'H'], reverse = True)[:9]
            return lineup, rotation, bullpen
