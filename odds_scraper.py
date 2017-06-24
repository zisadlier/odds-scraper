import urllib2
import requests
import time
from oddslib import *

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# Get a matchup list from a specified website and sport
def scrape(website, category):
	url = WEBSITES[website][category]

	if website not in WEBSITES.keys():
		print 'Invalid website'
	else:
		if category not in WEBSITES[website].keys():
			print 'Invalid category'

	if website == 'sportsbook':
		return get_matchups_sportsbook(url, 'lxml', category)
	if website == 'betus':
		return get_matchups_betus(url, 'lxml', category)
	if website == 'bovada':
		return get_matchups_bovada(url, 'lxml', category)

	return None

def make_soup_basic(url, parse_type):
	page = requests.get(url)
	soup = BeautifulSoup(page.text, parse_type)

	return soup

def make_soup_bovada(url, parse_type, chrome_path='C:/Python27/MyStuff/chromedriver.exe'):
	options = webdriver.ChromeOptions()
	options.add_argument('headless')

	browser = webdriver.Chrome(chrome_path, chrome_options=options)
	browser.get(url)


	body = browser.find_element_by_xpath('/html/body')
	body.send_keys(Keys.PAGE_DOWN)

	for i in range (0, 10):
		time.sleep(1)
		body.send_keys(Keys.PAGE_DOWN)
		i += 1

	WebDriverWait(browser, 10).until(EC.visibility_of_any_elements_located((By.TAG_NAME, "section")))

	html = browser.page_source
	browser.quit()

	soup = BeautifulSoup(html, parse_type)

	return soup

# Parse lines from a page on sportsbook.ag 
def get_matchups_sportsbook(url, parse_type, sport):
	soup = make_soup_basic(url, parse_type)

	elements = soup.find_all("div", id="_")
	matchups = []

	for element in elements:
		ls = element.get_text().split('\n')
		ls = [item.encode('ascii', 'ignore') for item in ls]
		ls = filter(lambda x: x != '', ls)
		if sport == "Baseball":
			del ls[1]
			del ls[5]

		t1 = ls[0]
		t2 = ls[4]

		temp = ls[2]
		s1 = Line('S', temp[:temp.find('(')], temp[temp.find('(')+1:temp.find(')')])

		temp = ls[6]
		s2 = Line('S', temp[:temp.find('(')], temp[temp.find('(')+1:temp.find(')')])

		temp = ls[3]
		m1 = Line('M', temp)

		temp = ls[7]
		m2 = Line('M', temp)

		temp = ls[1]
		o = None
		if temp == ' -':
			o = Line('O', temp)
		else:
			o = Line('O', temp[2:temp.find('(')], temp[temp.find('(')+1:temp.find(')')])

		temp = ls[5]
		u = None
		if temp == ' -':
			u = Line('U', temp)
		else:
			u = Line('U', temp[2:temp.find('(')], temp[temp.find('(')+1:temp.find(')')])

		matchup = Matchup(sport, 'Sportsbook', team_one=t1, team_two=t2, spread_one=s1, spread_two=s2,
	        		      mline_one=m1, mline_two=m2, over=o, under=u)

		matchups.append(matchup)


	return matchups


# Parse lines from a page on betus.com.pa
def get_matchups_betus(url, parse_type, sport):
	soup = make_soup_basic(url, parse_type)

	elements = soup.find_all("div", class_="show-pr")
	remove = ['uAdded', 'oAdded', 'Added']
	matchups = []

	for element in elements:
		ls = element.get_text().split('\n')
		ls = [item.encode('ascii', 'replace') for item in ls]

		for r in remove:
			ls = [item.replace(r, '') for item in ls]

		for i in range(0, len(ls)):
			ls[i] = filter(lambda x: ord(x) != 9 and ord(x) != 13, ls[i])
			ls[i] = ls[i].strip()
		ls = filter(lambda x: x != '', ls)
		ls = ls[3:-3]

		while len(ls) > 16:
			ls = ls[:-1]

		if len(ls) == 14:
			ls.insert(2, '-')
			ls.insert(12, '-')

		t1 = ls[0]
		t2 = ls[10]

		temp = ls[1].split()
		s1 = Line('S', temp[0].replace('?', '.5'), temp[1])

		temp = ls[11].split()
		s2 = Line('S', temp[0].replace('?', '.5'), temp[1])

		temp = ls[2]
		m1 = Line('M', temp)

		temp = ls[12]
		m2 = Line('M', temp)

		temp = ls[3]
		temp2 = ls[4]
		o = Line('O', temp.replace('?', '.5'), temp2)

		temp2 = ls[5]
		u = Line('U', temp.replace('?', '.5'), temp2)

		matchup = Matchup(sport, 'Betus', team_one=t1, team_two=t2, spread_one=s1, spread_two=s2,
	        		      mline_one=m1, mline_two=m2, over=o, under=u)

		matchups.append(matchup)

	return matchups #sorted(matchups, key=lambda matchup: str.lower(matchup.team_one[:3] + matchup.team_two[:3]))


# Parse lines from a page on bovada.lv
def get_matchups_bovada(url, parse_type, sport):		
	soup = make_soup_bovada(url, parse_type)

	elements = soup.find_all("section", class_="gameline-grid")
	matchups = []

	for element in elements:
		ls = element.get_text().split('\n')
		ls = [item.encode('ascii', 'replace') for item in ls]
		ls = filter(lambda x: x != '', ls)
		ls = ls[3:]
		
		t1 = ls[0]
		t2 = ls[1]

		temp = ls[3]
		s1 = Line('S', ls[2].replace('?', '.5'), temp[1:-1])

		temp = ls[5]
		s2 = Line('S', ls[4].replace('?', '.5'), temp[1:-1])

		temp = ls[6]
		m1 = Line('M', temp)

		temp = ls[7]
		m2 = Line('M', temp)

		temp = ls[8]
		temp2 = ls[9]
		o = Line('O', temp.replace('?', '.5'), temp2[1:-2])

		temp = ls[8]
		temp2 = ls[9]
		u = Line('U', temp.replace('?', '.5'), temp2[1:-2])

		matchup = Matchup(sport, 'Bovada', team_one=t1, team_two=t2, spread_one=s1, spread_two=s2,
	        		      mline_one=m1, mline_two=m2, over=o, under=u)

		matchups.append(matchup)

	return matchups

# Finds the most lopsided matchups of a set by either spread or money line
def get_worst_matchups(matchups, metric='spread'):
	largest_diff = 0
	worst_matchups = []

	for matchup in matchups:
		if metric == 'spread':
			spread = abs(matchup.spread_one.get_numerical_value())
			if largest_diff < spread:
				largest_diff = spread
				worst_matchups = []
				worst_matchups.append(matchup)
			elif largest_diff == spread:
				worst_matchups.append(matchup)

		if metric == 'mline':
			mline_diff = abs(matchup.mline_one.get_numerical_value()) + abs(matchup.mline_two.get_numerical_value())
			if largest_diff < mline_diff:
				largest_diff = mline_diff
				worst_matchups = []
				worst_matchups.append(matchup)
			elif largest_diff == mline_diff:
				worst_matchups.append(matchup)

	return worst_matchups

# Takes in a list of matchup lists and returns one list containing the average lines for every
# matchup appearing it at least one of the lists
def average_lines(matchup_lists):
	template = ['', '', [], [], [], [], [], []]
	average_matchups = {}
	final_matchups = []

	sport = matchup_lists[0][0].sport

	for matchups in matchup_lists:
		for matchup in matchups:
			key = matchup.get_key()
			if key not in average_matchups.keys():
				average_matchups[key] = template[:]
				average_matchups[key][0] = matchup.team_one 
				average_matchups[key][1] = matchup.team_two 
				average_matchups[key][2] = [matchup.spread_one.get_numerical_value(), matchup.spread_one.get_numerical_odds()]
				average_matchups[key][3] = [matchup.spread_two.get_numerical_value(), matchup.spread_two.get_numerical_odds()]
				average_matchups[key][4] = [matchup.mline_one.get_numerical_value(), matchup.mline_one.get_numerical_odds()]
				average_matchups[key][5] = [matchup.mline_two.get_numerical_value(), matchup.mline_two.get_numerical_odds()]
				average_matchups[key][6] = [matchup.over.get_numerical_value(), matchup.over.get_numerical_odds()]
				average_matchups[key][7] = [matchup.under.get_numerical_value(), matchup.under.get_numerical_odds()]
				#average_matchups[key][8] = 1
			else:
				average_matchups[key][2] = add_spreads(average_matchups[key][2], [matchup.spread_one.get_numerical_value(), matchup.spread_one.get_numerical_odds()])
				average_matchups[key][3] = add_spreads(average_matchups[key][3], [matchup.spread_two.get_numerical_value(), matchup.spread_two.get_numerical_odds()])
				average_matchups[key][4] = add_mlines(average_matchups[key][4], [matchup.mline_one.get_numerical_value(), matchup.mline_one.get_numerical_odds()])
				average_matchups[key][5] = add_mlines(average_matchups[key][5], [matchup.mline_two.get_numerical_value(), matchup.mline_two.get_numerical_odds()])
				average_matchups[key][6] = add_spreads(average_matchups[key][6], [matchup.over.get_numerical_value(), matchup.over.get_numerical_odds()])
				average_matchups[key][7] = add_spreads(average_matchups[key][7], [matchup.under.get_numerical_value(), matchup.under.get_numerical_odds()])
				#average_matchups[key][8] += 1

	for key, ls in average_matchups.iteritems():
		t1 = ls[0]
		t2 = ls[1]

		s1 = Line('S', ls[2][0], ls[2][1])
		s2 = Line('S', ls[3][0], ls[3][1])

		m1 = Line('M', ls[4][0])
		m2 = Line('M', ls[5][0])

		o = Line('O', ls[6][0], ls[6][1])
		u = Line('U', ls[7][0], ls[7][1])

		matchup = Matchup(sport, 'Average', team_one=t1, team_two=t2, spread_one=s1, spread_two=s2,
	        		      mline_one=m1, mline_two=m2, over=o, under=u)
		final_matchups.append(matchup)

	return final_matchups


# Prints out a list of matchups in a readable format
def print_nice(matchups):
	longest_name_length = 0
	for matchup in matchups:
		if len(matchup.team_one) > longest_name_length:
			longest_name_length = len(matchup.team_one)
		if len(matchup.team_two) > longest_name_length:
			longest_name_length = len(matchup.team_two)

	for matchup in matchups:
		longer_name_length = max(len(matchup.team_one), len(matchup.team_two))
		matchup.offset = (longest_name_length - longer_name_length) * ' '
		print('----------------------------------------------------------')
		print(matchup)


'''
m = scrape('betus', 'nfl')
m2 = scrape('sportsbook', 'nfl')
m3 = scrape('bovada', 'nfl')
mm = [m, m2, m3]
av = average_lines(mm)
'''