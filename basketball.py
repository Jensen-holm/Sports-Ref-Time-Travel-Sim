from scrape import ScrapeSR

class Basketball():

    def __init__(self, level = 'NBA'):
        self.TEAM1 = input('\nENTER TEAM 1 (ex: 2001 Pliledelphia 76ers): ')
        self.TEAM2 = input('\nENTER TEAM 2 (ex: 1980 Los Angeles Lakers):')
        self.level = level
        scraper = ScrapeSR('Basketball', self.TEAM1, self.TEAM2, self.level)