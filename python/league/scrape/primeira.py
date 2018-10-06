#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from league import league_shared

class PRIMEIRA(league_shared.TMSportsLeague):
    
    size_min = 900
    size_max = 1500

    divisions = [('https://www.transfermarkt.com/liga-nos/startseite/wettbewerb/PO1', 'Clubs - Liga NOS'), ('https://www.transfermarkt.com/ledman-liga-pro/startseite/wettbewerb/PO2', 'Clubs - Ledman Liga Pro')]
    
    def entities(self):
        return self.transfermarket(self.cv)            
