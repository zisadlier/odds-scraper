import requests
import time
import copy
import json

from oddslib import *
from params import *

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# Get a matchup list from a specified website and sport
def scrape(website, category):
	if website not in WEBSITES.keys():
		raise Exception('Invalid website')
	if category not in WEBSITES[website].keys():
		raise Exception('Invalid category')

	url = WEBSITES[website][category]

	if website == 'sportsbook':
		return get_matchups_sportsbook(url, 'html.parser', category)
	elif website == 'betus':
		return get_matchups_betus(url, 'html.parser', category)
	elif website == 'bovada':
		return get_matchups_bovada(url, 'html.parser', category)
	elif website == 'sportsbetting':
		return get_matchups_sportsbetting(url, 'html.parser', category)
	elif website == 'betlucky':
		return get_matchups_betlucky(url, 'html.parser', category)
	elif website == 'gtbets':
		return get_matchups_gtbets(url, 'html.parser', category)

	return None

def make_soup_basic(url, parse_type):
	page = requests.get(url)
	soup = BeautifulSoup(page.text, parse_type)

	return soup

def get_chrome_browser():
	options = webdriver.ChromeOptions()
	options.add_argument('headless')

	browser = webdriver.Chrome(chrome_path, chrome_options=options)

	return browser

def make_soup_bovada(url, parse_type):
	xpath_body = "/html/body"

	browser = get_chrome_browser()
	browser.get(url)

	body = browser.find_element_by_xpath(xpath_body)
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

def make_soup_sportsbetting(url, parse_type, sport):
	selector_tb = "tbody.event"
	xpath_body = "/html/body"

	selector_sport = SB_HTML_TOOLS[sport][0]
	xpath_sport = SB_HTML_TOOLS[sport][1]

	browser = get_chrome_browser()
	browser.get(url)
	body = browser.find_element_by_xpath(xpath_body)

	WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector_sport)))
	browser.find_element_by_css_selector(selector_sport).click()

	WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, xpath_sport)))
	browser.find_element_by_xpath(xpath_sport).click()
	time.sleep(1)

	WebDriverWait(browser, 10).until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, selector_tb)))
	html = browser.page_source
	browser.quit()

	soup = BeautifulSoup(html, parse_type)

	return soup

def make_soup_gtbets(url, parse_type):
	selector = 'tbody.wagering-events'

	browser = get_chrome_browser()
	browser.get(url)

	WebDriverWait(browser, 10).until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, selector)))
	html = browser.page_source
	browser.quit()

	soup = BeautifulSoup(html, parse_type)

	return soup


# Parse lines from a page on sportsbook.ag 
def get_matchups_sportsbook(url, parse_type, sport):
	print(add_color("Scraping lines from sportsbook.ag...", 'cyan'))
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
	print(add_color("Scraping lines from betus.com.pa...", 'cyan'))
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
	print(add_color("Scraping lines from bovada.lv...", 'cyan'))
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

def get_matchups_sportsbetting(url, parse_type, sport):
	print(add_color("Scraping lines from sportsbetting.ag...", 'cyan'))

	soup = make_soup_sportsbetting(url, parse_type, sport)

	elements = soup.find_all('tbody', class_='event')
	matchups = []

	for element in elements:
		ls = element.get_text().split('\n')
		ls = [item.encode('ascii', 'replace') for item in ls]
		ls = filter(lambda x: x != '' and x != 'o', ls)
		ls = [item.strip() for item in ls]
		ls = ls[2:]
		if ls == []:
			continue

		t1 = ls[0]
		t2 = ls[9]

		s1 = Line('S', ls[2].replace('?', '.5'), ls[3])
		s2 = Line('S', ls[11].replace('?', '.5'), ls[12])

		if ls[4] == '':
			ls[4] = '-'
		m1 = Line('M', ls[4])

		if ls[13] == '':
			ls[13] = '-'
		m2 = Line('M', ls[13])

		o = Line('O',ls[6].replace('?', '.5'), ls[7])
		u = Line('U',ls[15].replace('?', '.5'), ls[16])

		matchup = Matchup(sport, 'Sportsbetting', team_one=t1, team_two=t2, spread_one=s1, spread_two=s2,
	        		      mline_one=m1, mline_two=m2, over=o, under=u)

		matchups.append(matchup)

	return matchups

def get_matchups_betlucky(url, parse_type, sport):
	print(add_color("Scraping lines from betluckys.ag...", 'cyan'))

	soup = make_soup_basic(url, parse_type)

	elements = soup.find_all('tr')
	matchups = []
	disregard = ['Display:', 'Team']
	i = 0

	while(i < len(elements) - 1):
		ls = elements[i].get_text().split('\n')
		ls = [s.strip() for s in ls]
		ls = [item.encode('ascii', 'replace') for item in ls]
		ls = filter(lambda x: x != '', ls)
		if len(ls) < 2 or ls[0] in disregard:
			i += 1
			continue
		if ls[0][0].isdigit():
			ls = ls[1:]

		if ls[3][0] == 'O':
			ls.insert(3, '-')

		ls2 = elements[i + 1].get_text().split('\n')
		ls2 = [s.strip() for s in ls2]
		ls2 = [item.encode('ascii', 'replace') for item in ls2]
		ls2 = filter(lambda x: x != '', ls2)
		if len(ls2) < 2 or ls2[0] in disregard:
			i += 1
			continue
		if ls2[0][0].isdigit():
			ls2 = ls2[1:]

		if ls2[3][0] == 'U':
			ls2.insert(3, '-')

		t1 = ls[0]
		t2 = ls2[0]

		s1 = Line('S', ls[1].replace('?', '.5'), ls[2])
		s2 = Line('S', ls2[1].replace('?', '.5'), ls2[2])

		m1 = Line('M', ls[3])
		m2 = Line('M', ls2[3])

		o = Line('O',ls[4][1:].replace('?', '.5'), ls[5])
		u = Line('U',ls2[4][1:].replace('?', '.5'), ls2[5])

		matchup = Matchup(sport, 'Betlucky', team_one=t1, team_two=t2, spread_one=s1, spread_two=s2,
	        		      mline_one=m1, mline_two=m2, over=o, under=u)

		matchups.append(matchup)

		i += 2

	return matchups

def get_matchups_gtbets(url, parse_type, sport):	
	print(add_color("Scraping lines from gtbets.eu...", 'cyan'))

	soup = make_soup_gtbets(url, parse_type)

	elements = soup.find_all('tbody', class_='wagering-events')
	matchups = []

	for element in elements:
		ls = element.get_text().split('\n')
		ls = [item.encode('ascii', 'replace') for item in ls]
		ls = filter(lambda x: x != '', ls)
		ls = [item.strip() for item in ls]
		ls = ls[1:]

		t1 = ls[0]
		t2 = ls[5]

		temp = ls[1]
		s1 = Line('S', temp[:temp.find('(')], temp[temp.find('(')+1:temp.find(')')])

		temp = ls[6]
		s2 = Line('S', temp[:temp.find('(')], temp[temp.find('(')+1:temp.find(')')])

		m1 = Line('M', ls[2])
		m2 = Line('M', ls[7])

		temp = ls[3]
		if temp == '-':
			o = Line('O', temp, '')
		else:
			o = Line('O', temp[2:temp.find('(')], temp[temp.find('(')+1:temp.find(')')])

		temp = ls[8]
		if temp == '-':
			u = Line('U', temp, '')
		else:
			u = Line('U', temp[2:temp.find('(')], temp[temp.find('(')+1:temp.find(')')])

		matchup = Matchup(sport, 'GTBets', team_one=t1, team_two=t2, spread_one=s1, spread_two=s2,
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
def average_lines(matchup_lists, round=2):
	decimal = '{0:.' + str(round) + 'f}'
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
			else:
				average_matchups[key][2] = add_spreads(average_matchups[key][2], [matchup.spread_one.get_numerical_value(), matchup.spread_one.get_numerical_odds()], decimal)
				average_matchups[key][3] = add_spreads(average_matchups[key][3], [matchup.spread_two.get_numerical_value(), matchup.spread_two.get_numerical_odds()], decimal)
				average_matchups[key][4] = add_mlines(average_matchups[key][4], [matchup.mline_one.get_numerical_value(), matchup.mline_one.get_numerical_odds()], decimal)
				average_matchups[key][5] = add_mlines(average_matchups[key][5], [matchup.mline_two.get_numerical_value(), matchup.mline_two.get_numerical_odds()], decimal)
				average_matchups[key][6] = add_spreads(average_matchups[key][6], [matchup.over.get_numerical_value(), matchup.over.get_numerical_odds()], decimal)
				average_matchups[key][7] = add_spreads(average_matchups[key][7], [matchup.under.get_numerical_value(), matchup.under.get_numerical_odds()], decimal)

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

def get_deviation(matchup_one, matchup_two, metric):
	deviation = 0

	if metric == 'spread':
		deviation = abs(abs(matchup_one.spread_one.get_numerical_value()) - abs(matchup_two.spread_one.get_numerical_value()))
	elif metric == 'mline':
		diff_one = abs(matchup_one.mline_one.get_numerical_value()) + abs(matchup_one.mline_two.get_numerical_value())
		diff_two = abs(matchup_two.mline_one.get_numerical_value()) + abs(matchup_two.mline_two.get_numerical_value())
		deviation = abs(diff_one - diff_two)

	return deviation

def find_largest_deviants(average_matchups, matchup_lists, metric):
	largest_deviants = []
	for i in range(len(average_matchups)):
		largest_deviants.append(None)

	for i, average_matchup in enumerate(average_matchups):
		largest_dev = -1;
		for matchups in matchup_lists:
			for matchup in matchups:
				if average_matchup.get_key() == matchup.get_key():
					dev = None

					if metric == 'spread':
						dev = get_deviation(average_matchup, matchup, 'spread')
					if metric == 'mline':
						dev = get_deviation(average_matchup, matchup, 'mline')

					if dev == largest_dev and largest_deviants[i] != None:
						largest_deviants[i].add_website(matchup.website)

					if dev > largest_dev:
						largest_deviants[i] = copy.deepcopy(matchup)
						largest_dev = dev

					break

	return largest_deviants



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

def json_dump(matchups_list, fname):
	site_dict = {}
	site_dict['date'] = time_string('day')

	for matchups in matchups_list:
		matchups_dict = {}
		site_dict[matchups[0].website] = matchups_dict
		for matchup in matchups:
			di = {}

			di['sport']  = matchup.sport
			di['website'] = matchup.website
			di['team one'] = matchup.team_one
			di['team two'] = matchup.team_two
			di['spread one'] = matchup.spread_one.get_string()
			di['spread two'] = matchup.spread_two.get_string()
			di['mline one'] = matchup.mline_one.get_string()
			di['mline two'] = matchup.mline_two.get_string()
			di['over'] = matchup.over.get_string()
			di['under'] = matchup.over.get_string()

			matchups_dict[matchup.get_key()] = di

	with open(fname, 'w') as f:
		json.dump(site_dict, f)

def json_load(fname):
	matchups_list = []
	site_dict = {}

	with open(fname, 'r') as f:
		site_dict = json.load(f)

	matchups_list.append(site_dict['date'])

	for site in site_dict.keys():
		if site == 'date':
				continue

		matchups_dict = site_dict[site]
		matchups = []
		for key in matchups_dict.keys():

			di = matchups_dict[key]

			sport = di['sport']
			website = di['website']
			t1 = di['team one']
			t2 = di['team two']
			s1 = di['spread one']
			s2 = di['spread two']
			m1 = di['mline one']
			m2 = di['mline two']
			o = di['over']
			u = di['under']

			matchup = Matchup(sport, website, team_one=t1, team_two=t2, spread_one=s1, spread_two=s2,
	        		      mline_one=m1, mline_two=m2, over=o, under=u)

			matchups.append(matchup)

		matchups_list.append(matchups)

	return matchups_list


def time_string(kind):
	import datetime

	now = datetime.datetime.now()
	if kind == 'day':
		return now.strftime("%m-%d-%Y")
	if kind == 'time':
		return now.strftime("%H:%M:%S")

def generate_html_file_matchups(matchups, file_name):
	from yattag import Doc
	from yattag import indent

	doc, tag, text, line = Doc().ttl()

	doc.asis('<!DOCTYPE html>')
	with tag('html'):
		with tag('body'):
			line('p', time_string('day'))
			line('p', time_string('time'))
			line('h1', 'Lines')
			with tag('head'):
				doc.stag('link', rel='stylesheet', href='style.css')
			for matchup in matchups:
				with tag('table'):
					with tag('tr'):
						line('td', matchup.website, rowspan=3, klass='site')
						line('th', 'Team')
						line('th', 'Spread')
						line('th', 'Money Line')
						line('th', 'O/U')					
					with tag('tr'):
						line('td', matchup.team_one)
						line('td', matchup.spread_one.get_string())
						line('td', matchup.mline_one.get_string())
						line('td', matchup.over.get_string(), rowspan=2)
					with tag('tr'):
						line('td', matchup.team_two)
						line('td', matchup.spread_two.get_string())
						line('td', matchup.mline_two.get_string())

	file = open(file_name, 'w')
	file.write(indent(doc.getvalue()))


def generate_html_file_with_deviants(average_matchups, deviant_spreads, deviant_mlines, file_name):
	from yattag import Doc
	from yattag import indent

	doc, tag, text, line = Doc().ttl()

	doc.asis('<!DOCTYPE html>')
	with tag('html'):
		with tag('body'):
			line('p', time_string('day'))
			line('p', time_string('time'))
			line('h1', 'Lines and largest deviants')
			with tag('head'):
				doc.stag('link', rel='stylesheet', href='style.css')
			for i, matchup in enumerate(average_matchups):
				deviant_spread = deviant_spreads[i]
				deviant_mline = deviant_mlines[i]
				with tag('table'):
					with tag('tr'):
						with tag('td', klass='outer'):
							with tag('table'):
								with tag('tr'):
									line('td', matchup.website, rowspan=3, klass='site')
									line('th', 'Team')
									line('th', 'Spread')
									line('th', 'Money Line')
									line('th', 'O/U')					
								with tag('tr'):
									line('td', matchup.team_one)
									line('td', matchup.spread_one.get_string())
									line('td', matchup.mline_one.get_string())
									line('td', matchup.over.get_string(), rowspan=2)
								with tag('tr'):
									line('td', matchup.team_two)
									line('td', matchup.spread_two.get_string())
									line('td', matchup.mline_two.get_string())
						with tag('td', klass='outer'):
							with tag('table'):
								with tag('tr'):
									line('td', deviant_spread.website, rowspan=3, klass='site')
									line('th', 'Spread', klass='deviant')			
								with tag('tr'):
									line('td', deviant_spread.spread_one.get_string())
								with tag('tr'):
									line('td', deviant_spread.spread_two.get_string())
						with tag('td', klass='outer'):
							with tag('table'):
								with tag('tr'):
									line('td', deviant_mline.website, rowspan=3, klass='site')
									line('th', 'Money Line', klass='deviant')				
								with tag('tr'):
									line('td', deviant_mline.mline_one.get_string())
								with tag('tr'):
									line('td', deviant_mline.mline_two.get_string())

	file = open(file_name, 'w')
	file.write(indent(doc.getvalue()))

"""
m = [scrape('betus', 'nfl')]
json_dump(m, 'test.json')
mm = json_load('test.json')
"""