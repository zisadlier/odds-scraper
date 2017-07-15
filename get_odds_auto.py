from odds_scraper import *
from oddslib import WEBSITES
from pyvirtualdisplay import Display

display = Display(visible=0, size=(1024, 768))
display.start()

sites = [site for site in WEBSITES.keys()]

matchup_lists = []

for site in sites:
	matchups = scrape(site, 'nfl')
	matchup_lists.append(matchups)

averaged = average_lines(matchup_lists)
deviant_spreads = find_largest_deviants(averaged, matchup_lists, 'spread')	
deviant_mlines = find_largest_deviants(averaged, matchup_lists, 'mline')

generate_html_file_with_deviants(averaged, deviant_spreads, deviant_mlines, 'lines.html')

display.stop()	
