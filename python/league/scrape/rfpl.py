from league import league_shared

class RFPL(league_shared.TMSportsLeague):
    
    min_size = 900
    max_size = 1300
    
    divisions = [('https://www.transfermarkt.com/premier-liga/startseite/wettbewerb/RU1', 'Clubs - Premier Liga'), 
                 ('https://www.transfermarkt.com/1-division/startseite/wettbewerb/RU2', 'Clubs - 1.Division')]
    
    def filter_tweet(self, msg):
        return True
    
    def entities(self):
        return self.transfermarket(self.cv)