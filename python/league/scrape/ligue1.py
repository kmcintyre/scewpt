from league import league_shared

class LIGUE1(league_shared.TMSportsLeague):
    
    min_size = 900
    max_size = 1300
    
    divisions = [('https://www.transfermarkt.com/ligue-1/startseite/wettbewerb/FR1', 'Clubs - Ligue 1'), ('https://www.transfermarkt.com/jumplist/startseite/wettbewerb/FR2', 'Clubs - Ligue 2')]
    
    def entities(self):
        return self.transfermarket(self.cv)