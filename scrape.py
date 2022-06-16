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
    def find_link(self, url, link_text, second_check = False):
        if second_check == True:
            if self.team1yr == '2022' and self.level.lower() == 'other':
                html = BeautifulSoup(requests.get(url).text, features= 'lxml')
                year, name, num_teams = self.sewp_info(html)
                num_teams = int(num_teams)
                s = "".join(c for c in html.find_all(text=Comment) if "table_container" in c)
                soup = BeautifulSoup(s, "html.parser")
                team_links = [('https://baseball-reference.com' + a['href']) for a in soup.select('[href*="/register/team.cgi?id="]')][:num_teams]
                return team_links
            # if self.team2yr == '2022' and self.level.lower() == 'other':
            #     year, name, num_teams = self.sewp_info(BeautifulSoup(requests.get(url).text, features = 'lxml'))

        elif second_check == False:
            # if self.team1yr != '2022' and self.team2yr != '2022':
                html = BeautifulSoup(requests.get(url).text, features = 'lxml')
                a_tags = html.find_all('a', href = True)
                return [link['href'] for link in a_tags if link.text == link_text]

    def parse_row(self, row):
        return [str(x.string) for x in row.find_all('td')]

    def sewp_info(self, html):
        spans = html.find_all('span')
        p_tags = html.find_all('p')
        return spans[8].text, spans[9].text, p_tags[1].text.split()[3]

    ''' ------------------------------- Baseball Specific Functions ---------------------------------- '''
    def find_baseball_data(self, url):
        # html = BeautifulSoup(requests.get(url).text, features = 'lxml')

        # # parsing columns
        # th_tags = html.find_all('th', attrs = {'scope':'col'})
        # lst = [th.text for th in th_tags]
        # joined = ' '.join(lst).split('Rk') # we can get Rk out of the cols since it acts as the index
        # all_cols = [lisst.split() for lisst in joined][1:]

        # pitching data hidden in comments for 'other' leagues (northwoods league for sure)

        if self.level.lower() == 'mlb':
            # hit_cols = all_cols[0]
            # pit_cols = all_cols[1]
            # # parsing data 
            # tables = html.find_all('table')
            # tr = [table.find_all('tr') for table in tables]
            hitting_data = pd.read_html(url)[0].dropna(how = 'all').fillna(0)
            pitching_data = pd.read_html(url)[1].dropna(how = 'all').fillna(0)

            hitting_data = hitting_data[hitting_data['Name'] != 'Name']
            pitching_data = pitching_data[pitching_data['Name'] != 'Name']

            hitting_data['Name'] = hitting_data['Name'].str.replace('*', '', regex = False)
            hitting_data['Name'] = hitting_data['Name'].str.replace('#', '', regex = False)

            pitching_data['Name'] = pitching_data['Name'].str.replace('*', '')
            pitching_data['Name'] = pitching_data['Name'].str.replace('#', '')

        elif self.level.lower() == 'other':
            # find pitching data in the comments
            hitting_data = pd.read_html(url)[0].dropna(how = 'all').fillna(0)
            hitting_data['Name'] = hitting_data['Name'].str.replace('*', '').str.replace('#', '')
            soup = BeautifulSoup(requests.get(url).text,'lxml')
            pitching_data = pd.read_html([x for x in soup.find_all(string=lambda text: isinstance(text, Comment)) if 'id="div_team_pitching"' in x][0])[0]
            pitching_data['Name'] = pitching_data['Name'].str.replace('*', '').str.replace('#', '')

        # in the future we should include statcast data and probs if the years are 2015 or later

        return hitting_data, pitching_data, hitting_data.columns, pitching_data.columns

    # sport specific functions
    def baseball(self):
        default_url = 'https://baseball-reference.com'

        if self.level.lower() == 'other':
            league_link = default_url + self.find_link(default_url + '/register/', self.league)[0]

            ''' need to make a new find link function for 2022 where we test every link until it matches the link text using sewp info '''
            if self.team1yr == '2022' and self.level.lower() == 'other':

                yr_link1 = self.find_link(league_link, self.team1yr)[2]
                team_links = self.find_link(default_url + yr_link1, self.team1, second_check= True)
                the_link = []
                # try em all
                for link in team_links:
                    html = BeautifulSoup(requests.get(link).text, features = 'lxml')
                    yr, name, num_teams = self.sewp_info(html)
                    if name == self.team1:
                        the_link.append(link)
                hit1, pit1, hit_cols, pit_cols = self.find_baseball_data(the_link[0])


            if self.team2yr == '2022' and self.level.lower() == 'other':
                yr_link1 = self.find_link(league_link, self.team1yr)[2]
                team_links = self.find_link(default_url + yr_link1, self.team1, second_check= True)
                the_link = []
                # try em all
                for link in team_links:
                    html = BeautifulSoup(requests.get(link).text, features = 'lxml')
                    yr, name, num_teams = self.sewp_info(html)
                    if name == self.team2:
                        the_link.append(link)
                hit2, pit2, hit_cols, pit_cols = self.find_baseball_data(the_link[0])


            if self.team1yr != '2022' and self.team2yr != '2022':
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
