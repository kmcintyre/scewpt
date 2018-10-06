from league import league_shared

class CSL(league_shared.TMSportsLeague):
    
    min_size = 800
    max_size = 1200      
    
    divisions = [('https://www.transfermarkt.com/chinese-super-league/startseite/wettbewerb/CSL', 'Clubs - Chinese Super League'), ('https://www.transfermarkt.com/china-league-one/startseite/wettbewerb/CLO', 'Clubs - China League One')]
    
    def entities(self):
        return self.transfermarket(self.cv)