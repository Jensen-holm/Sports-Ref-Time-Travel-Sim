from nwl_righty_lefty import splits
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
        self.hit1, self.pit1, self.hit2, self.pit2, self.hit_cols, self.pit_cols = self.baseball()

        ''' go to northwoods league page for split stats if self.league == 'northwoods league' '''

        # if self.league.strip().lower() == 'northwoods league':
        #     nwl_scraper = splits()
        #     self.team1 = nwl_scraper.team1()
        #     self.team2 = nwl_scraper.team2()

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
    def find_baseball_data(self, url, teamyr = ''):

        if self.level.lower() == 'mlb':

            if teamyr != '2022':
                hitting_data = pd.read_html(url)[0].dropna(how = 'all').fillna(0)
                pitching_data = pd.read_html(url)[1].dropna(how = 'all').fillna(0)
            elif teamyr == '2022':
                # have to change the index because of the schedule tables in the current season
                hitting_data = pd.read_html(url)[-2].dropna(how = 'all').fillna(0)
                pitching_data = pd.read_html(url)[-1].dropna(how = 'all').fillna(0)

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
        def_url_other = 'https://www.baseball-reference.com/register/league.cgi'

        if self.level.lower() == 'other':

            league_link = default_url + self.find_link(def_url_other, self.league)[0]

            if self.team1yr == '2022':

                yr_link1 = self.find_link(league_link, self.team1yr)[2]
                team_links = self.find_link(default_url + yr_link1, self.team1, second_check= True)
                the_link = []
                # try em all
                for link in team_links:
                    html = BeautifulSoup(requests.get(link).text, features = 'lxml')
                    yr, name, num_teams = self.sewp_info(html)
                    if name == self.team1:
                        the_link.append(link)
                        break
                hit1, pit1, hit_cols, pit_cols = self.find_baseball_data(the_link[0])


            if self.team2yr == '2022':
                yr_link1 = self.find_link(league_link, self.team1yr)[2]
                team_links = self.find_link(default_url + yr_link1, self.team1, second_check= True)
                the_link = []
                # try em all
                for link in team_links:
                    html = BeautifulSoup(requests.get(link).text, features = 'lxml')
                    yr, name, num_teams = self.sewp_info(html)
                    if name == self.team2:
                        the_link.append(link)
                        break
                hit2, pit2, hit_cols, pit_cols = self.find_baseball_data(the_link[0])

            if self.team1yr != '2022':
                yr_link1 = default_url + self.find_link(league_link, self.team1yr)[2]
                team1_link = default_url + self.find_link(yr_link1, self.team1)[0]
                hit1, pit1, hit_cols, pit_cols = self.find_baseball_data(team1_link)

            if self.team2yr != '2022':
                yr_link2 = default_url + self.find_link(league_link, self.team2yr)[2]
                team2_link = default_url + self.find_link(yr_link2, self.team2)[0]
                hit2, pit2, hit_cols, pit_cols = self.find_baseball_data(team2_link)

            if self.team1yr != '2022' and self.team2yr != '2022':
                yr_link1 = default_url + self.find_link(league_link, self.team1yr)[2]
                yr_link2 = default_url + self.find_link(league_link, self.team2yr)[2]

                team1_link = default_url + self.find_link(yr_link1, self.team1)[0]
                team2_link = default_url + self.find_link(yr_link2, self.team2)[0]

                hit1, pit1, hit_cols, pit_cols = self.find_baseball_data(team1_link)
                hit2, pit2, hit_cols, pit_cols = self.find_baseball_data(team2_link)
            return hit1, pit1, hit2, pit2, hit_cols, pit_cols
            
        # mlb branch
        elif self.team1yr != '2022' and self.team2yr != '2022':
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
        
        # 2022 mlb branch since the current season html is different
        elif self.level.lower() == 'mlb' and self.team1yr == '2022' or self.team2yr == '2022':
            def_url = 'https://www.baseball-reference.com/leagues/majors/2022.shtml'

            # team1
            if self.team1yr == '2022':
                link1 = default_url + self.find_link(def_url, self.team1)[0]
                hit1, pit1, hit_cols, pit_cols = self.find_baseball_data(link1, teamyr = self.team1yr)

            elif self.team1yr != '2022':
                # find year links for each team
                yr_link1 = default_url + self.find_link('https://www.baseball-reference.com/leagues/', self.team1yr)[0]
                # find team links for each team
                team1_link = default_url + self.find_link(yr_link1, self.team1)[0]
                # get probability data from each team link
                hit1, pit1, hit_cols, pit_cols = self.find_baseball_data(team1_link)

            if self.team2yr == '2022':
                link2 = default_url + self.find_link(def_url, self.team2)[0]
                hit2, pit2, hit_cols, pit_cols = self.find_baseball_data(link2, teamyr = self.team2yr)

            elif self.team2yr != '2022':
            # find year links for each team
                yr_link2 = default_url + self.find_link('https://www.baseball-reference.com/leagues/', self.team2yr)[0]
                # find team links for each team
                team2_link = default_url + self.find_link(yr_link2, self.team2)[0]
                # get probability data from each team link
                hit2, pit2, hit_cols1, pit_cols1 = self.find_baseball_data(team2_link)
            
            return hit1, pit1, hit2, pit2, hit_cols, pit_cols
