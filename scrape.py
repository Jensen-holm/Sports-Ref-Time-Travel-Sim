''' Scrape Sports Reference with the goal of simulation in mind '''
from bs4 import BeautifulSoup, Comment
import pandas as pd
import requests

class ScrapeSR():

    def __init__(self, sport, league, team1, team2, level):
        # these are inputs taken from another file, we clean up the input within those files
        self.league = league
        self.sport = sport
        self.team1 = team1[5:].strip()
        self.team2 = team2[5:].strip()
        self.team1yr = team1[:5].strip()
        self.team2yr = team2[:5].strip()
        self.level = level

        if self.sport == 'Baseball':
            self.hit1, self.pit1, self.hit2, self.pit2, self.hit_cols, self.pit_cols = self.baseball()
        elif self.sport.lower() != 'baseball':
            print('\n\nSCRAPER ONLY CAPEABLE OF BASEBALL AT THE MOMENT.')

    ''' ----------------------------------- Scraping Functions --------------------------------------- '''
    def find_link(self, url, link_text):
        html = BeautifulSoup(requests.get(url).text, features = 'lxml')
        a_tags = html.find_all('a', href = True)
        return [link['href'] for link in a_tags if link.text == link_text]

    def parse_row(self, row):
        return [str(x.string) for x in row.find_all('td')]

    ''' ------------------------------- Baseball Specific Functions ---------------------------------- '''
    def find_baseball_data(self, url):
        html = BeautifulSoup(requests.get(url).text, features = 'lxml')

        # parsing columns
        th_tags = html.find_all('th', attrs = {'scope':'col'})
        lst = [th.text for th in th_tags]
        joined = ' '.join(lst).split('Rk') # we can get Rk out of the cols since it acts as the index
        all_cols = [lisst.split() for lisst in joined][1:]

        # pitching data hidden in comments for 'other' leagues (northwoods league for sure)

        if self.level.lower() == 'mlb':
            hit_cols = all_cols[0]
            pit_cols = all_cols[1]
        elif self.level.lower() == 'other':
            hit_cols = all_cols[0]

            # find pitching data in the comments

        # parsing data 
        tables = html.find_all('table')
        tr = [table.find_all('tr') for table in tables]
        hitting_data = pd.DataFrame([self.parse_row(row) for row in tr[0]], columns = hit_cols).dropna(how = 'all')
        pitching_data = pd.DataFrame([self.parse_row(row) for row in tr[1]], columns = pit_cols).dropna(how = 'all')

        # parse fielding data out from the html comments at some point?
        # in the future we should include statcast data if the years are 2015 or later

        return hitting_data, pitching_data, hit_cols, pit_cols

    # sport specific functions
    def baseball(self):
        default_url = 'https://baseball-reference.com'

        if self.level.lower() == 'other':
            league_link = default_url + self.find_link(default_url + '/register/', self.league)[0]
            
            yr_link1 = default_url + self.find_link(league_link, self.team1yr)[2]
            yr_link2 = default_url + self.find_link(league_link, self.team2yr)[2]

            team1_link = default_url + self.find_link(yr_link1, self.team1)[0]
            team2_link = default_url + self.find_link(yr_link2, self.team2)[0]

            hit1, pit1, hit_cols, pit_cols = self.find_baseball_data(team1_link)
            hit2, pit2, hit_cols, pit_cols = self.find_baseball_data(team2_link)
            return hit1, pit1, hit2, pit2, hit_cols, pit_cols
            
        elif self.level.lower() == 'mlb':
            # find year links for each team
            yr_link1 = default_url + self.find_link('https://www.baseball-reference.com/leagues/', self.team1yr)[0]
            yr_link2 = default_url + self.find_link('https://www.baseball-reference.com/leagues/', self.team2yr)[0]

            # find team links for each team
            team1_link = default_url + self.find_link(yr_link1, self.team1)[0]
            team2_link = default_url + self.find_link(yr_link2, self.team2)[0]

            # get probability data from each team link
            hit1, pit1, hit_cols, pit_cols = self.find_baseball_data(team1_link)
            hit2, pit2, hit_cols1, pit_cols1 = self.find_baseball_data(team2_link)

            return hit1, pit1, hit2, pit2, hit_cols, pit_cols
