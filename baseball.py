from scrape import ScrapeSR
import pandas as pd
import random

class Player():

    def __init__(self, df_row, hitter):
        self.df = df_row
        self.hitter = hitter
        print(self.df)

        self.df = self.df.apply(pd.to_numeric, errors = 'coerce').combine_first(self.df)

        if hitter == True:
            self.hitter_probs()
        elif self.hitter == False:
            self.pitcher_probs()

        # keep track of stats over simulation
        # if they're a hitter
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

        # stats unique to pitchers
        if self.hitter == False:
            self.IP = 0
            self.BF = 0
            self.ER = 0
            self.R = 0

    ''' ----------------------------- Probability and stat functions --------------------------------- '''
    # call the rate stats funciton when the simulations are over
    def rate_stats(self):
        if self.hitter == True:
            self.OPS = self.OBP + self.SLG
            self.BA = self.H / self.at_bats
        elif self.hitter == False:
            self.WHIP = self.BB + self.H / self.IP
            self.ERA = (9 * self.ER) / self.IP
            self.HR_9 = self.HR / (self.IP / 9)
            self.K_9 = self.K / (self.IP / 9)
            self.BB_9 = self.BB / (self.IP / 9)
            self.BB_K = self.BB / self.K
                
    def pitcher_probs(self):
        # probabilities on a PA basis
        self.K = self.df['SO'] / self.df['BF']
        self.BB = self.df['BB'] / self.df['BF'] + self.K
        self.H = self.df['H'] / self.df['BF'] + self.BB
        self.HBP = self.df['HBP'] / self.df['BF'] + self.H
        self.IPO = 1 - (self.K + self.BB + self.H + self.HBP)

    def hitter_probs(self):
        # add single column (p is for probabillity)
        if self.df['PA'] > 0 and self.df['H'] > 0:
            self.df['1B'] = self.df['H'] - self.df['2B'] - self.df['3B'] - self.df['HR']

            # probabilities on a PA basis, check at some point if it adds up to 1
            self.Kp = self.df['SO'] / self.df['PA']
            self.BBp = self.df['BB'] / self.df['PA'] + self.Kp
            self.Hp = self.df['H'] / self.df['PA'] + self.Kp + self.BBp
            self.HBPp = self.df['HBP'] / self.df['PA'] + self.Kp + self.BBp + self.Hp
            self.IPOp = 1 - (self.Kp + self.BBp + self.Hp + self.HBPp)

            # if they get a hit, these are the probabilities of how many bases they get
            self.singlep = self.df['1B'] / self.df['H']
            self.doublep = self.df['2B'] / self.df['H'] + self.singlep
            self.triplep = self.df['3B'] / self.df['H'] + self.singlep + self.doublep
            self.HRp = self.df['HR'] / self.df['H'] + self.singlep + self.doublep + self.triplep

        ''' SB is giving me problems with string values somehow '''
        # # in this sim we are only going to go with simulating SB from 1b
        # if self.df['SB'] > 0 and self.df['1B'] > 0 and self.df['CS'] > 0:
        #     self.ATTSBp =  self.df['SB'] + self.df['CS'] / self.df['1B']
        #     self.SBp = self.df['SB'] / self.df['SB'] + self.df['CS']
        #     self.CSp = self.df['CS'] / self.df['SB'] + self.df['CS'] + self.SBp


class Team():

    def __init__(self, hit_df, pit_df):
        self.hit_prob = hit_df
        self.pit_prob = pit_df
        self.hitters, self.pitchers = self.generate_players()

        self.lineup = [hitter for hitter in self.hitters][:10]
        self.rotation = [pitcher for pitcher in self.pitchers][:6]
        
    def generate_players(self):
        hitters = [Player(self.hit_prob.iloc[i], hitter = True) for i in range(len(self.hit_prob))]
        pitchers = [Player(self.pit_prob.iloc[i], hitter = False) for i in range(len(self.pit_prob))]
        return hitters, pitchers



class Baseball():

    def __init__(self, level = 'MLB'):

        self.TEAM1 = input('\nENTER TEAM 1 (ex: 1899 Cincinnati Reds): ').title().strip()
        self.TEAM2 = input('ENTER TEAM 2 (ex: 2015 Kansas City Royals): ').title().strip()

        self.level = level
        scraper = ScrapeSR('Baseball', self.TEAM1, self.TEAM2, self.level)

        self.team1hit, self.team2hit = scraper.hit1, scraper.hit2
        self.team1pit, self.team2pit = scraper.pit1, scraper.pit2

        Team1, Team2 = Team(self.team1hit, self.team1hit), Team(self.team2hit, self.team2hit)

        self.num_sims = int(input('\nENTER NUMBER OF SIMULATIONS: '))

        for i in range(self.num_sims):
            for i in range(9):
                self.half_inning(Team1, Team2)
                self.half_inning(Team2, Team1)

        ''' -------------------------------- Baseball Game Functions ------------------------------------- '''
    def PA(self, hitter, pitcher):
        # decide the outcome of a plate appearance
        # then log the result to the player and team metrics
        num = random.random()
        # check if the num is between the least probable outcome and 0
        outcomes = ['K', 'BB', 'H', 'IPO', 'HBP']
        lst = zip([hitter.Kp + pitcher.Kp, hitter.BBp + pitcher.BBp,hitter.Hp + pitcher.Hp, hitter.IPOp + pitcher.IPOp, hitter.HBPp + pitcher.HBPp], outcomes) # hopefully this adds up to 2?
        # sort it by least probable to most probable
        lst.sort()
        print(lst)
        return

    def half_inning(self, pitching_team, hitting_team):
        outs = 0
        while outs < 3:

            index = 0
            self.PA(hitting_team.lineup[index], pitching_team.rotation[0])
            index += 1


            outs += 1

        return