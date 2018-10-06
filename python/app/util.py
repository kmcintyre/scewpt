def league_class(league_name):
    mod = __import__('league.scrape.' + league_name, fromlist=[''])
    league = getattr(mod, league_name.upper())
    return league()