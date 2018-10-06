from league import league_shared

class SERIEA(league_shared.TMSportsLeague):
    
    min_size = 1100
    max_size = 1600      
    
    divisions = [('https://www.transfermarkt.com/serie-a/startseite/wettbewerb/IT1', 'Clubs - Serie A'), ('https://www.transfermarkt.com/serie-b/startseite/wettbewerb/IT2', 'Clubs - Serie B')]
    
    def entities(self):
        return self.transfermarket(self.cv)
