import sys
import webbrowser

from odds_scraper import *
from oddslib import WEBSITES


def main():
	sports = ['nba', 'nfl', 'ncaaf']
	websites = [site for site in WEBSITES.keys()] + ['all']

	#Ask for which sport to scrape for
	sport = raw_input('Enter a sport to scrape for: ').strip()
	if sport not in sports:
		raise Exception('Invalid sport')

	#Get websites to scrape
	sites = raw_input('Enter websites to scrape, separate by space: ').strip()
	sites = sites.split()
	if sites[0] == 'all':
		sites = websites[:-1]

	deviant = 'n'

	#If more than one website specified, ask about getting a deviant list
	if len(sites) > 1:
		deviant = raw_input('Generate a largest deviant list too? (y/n): ').strip()
		if deviant not in ['n', 'y']:
			raise Exception('Invalid response')

	matchup_lists = []

	#Scrape each specified website
	for site in sites:
		if site not in websites:
			raise Exception('Invalid website: ' + site)

		matchups = scrape(site, sport)
		matchup_lists.append(matchups)

	final_list = []
	if len(matchup_lists) == 1:
		if '-v' in sys.argv:
			print_nice(matchup_lists[0])
		final_list = matchup_lists[0]
	else:
		averaged = average_lines(matchup_lists)
		if '-v' in sys.argv:
			print_nice(averaged)
		final_list = averaged

	if deviant == 'y':
		deviants_spreads = find_largest_deviants(averaged, matchup_lists, 'spread')
		deviants_mlines = find_largest_deviants(averaged, matchup_lists, 'mline')
		generate_html_file_with_deviants(final_list, deviants_spreads, deviants_mlines, 'lines.html')
	else:
		generate_html_file_matchups(final_list, 'lines.html')

	#Open the generated html file
	webbrowser.open_new_tab('lines.html')

if __name__=="__main__":
	main()

