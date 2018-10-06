from league import league_shared

class BUNDESLIGA(league_shared.TMSportsLeague):

    min_size = 900
    max_size = 1300
    
    divisions = [('https://www.transfermarkt.com/1-bundesliga/startseite/wettbewerb/L1', 'Clubs - 1.Bundesliga'), ('https://www.transfermarkt.com/2-bundesliga/startseite/wettbewerb/L2', 'Clubs - 2.Bundesliga')]
    
    def entities(self):
        return self.transfermarket(self.cv)