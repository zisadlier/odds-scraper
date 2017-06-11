import urllib2
import requests
import time
from oddslib import Line, Matchup, WEBSITES

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def scrape(website, category):
	url = WEBSITES[website][category]

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
		#s1 = None
		#if temp == ' -':
		#	s1 = Line('S', temp)
		#else:
		s1 = Line('S', temp[:temp.find('(')], temp[temp.find('(')+1:temp.find(')')])

		temp = ls[6]
		#s2 = None
		#if temp == ' -':
		#	s2  = Line('S', temp)
		#else:
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

		matchup = Matchup(sport, 'Betus', team_one=t1, team_two=t2, spread_one=s1, spread_two=s2,
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

		matchup = Matchup(sport, 'Sportsbook', team_one=t1, team_two=t2, spread_one=s1, spread_two=s2,
	        		      mline_one=m1, mline_two=m2, over=o, under=u)

		matchups.append(matchup)

	return matchups


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


def get_worst_matchups(matchups, metric):
	largest_diff = 0
	worst_matchups = []

	for matchup in matchups:
		if metric == 1:
			spread = abs(matchup.spread_one.get_numerical_value())
			if largest_diff < spread:
				largest_diff = spread
				worst_matchups = []
				worst_matchups.append(matchup)
			elif largest_diff == spread:
				worst_matchups.append(matchup)

		if metric == 2:
			mline_diff = abs(matchup.mline_one.get_numerical_value()) + abs(matchup.mline_two.get_numerical_value())
			if largest_diff < mline_diff:
				largest_diff = mline_diff
				worst_matchups = []
				worst_matchups.append(matchup)
			elif largest_diff == mline_diff:
				worst_matchups.append(matchup)

	print_nice(worst_matchups)

def print_nice(matchups):
	for matchup in matchups:
		print '----------------------------------------------------------'
		print matchup



'''
s1 = Line('S', '-1.5', '+125')
m1 = Line('M', '-127',)
o = Line('O', '8.5', '-115')
s2 = Line('S', '+1.5', '-145')
m2 = Line('M', '+117',)
u = Line('U', '8.5', '-105')

M = Matchup('Baseball', 'Sportsbook', team_one='Toronto Blue Jays', team_two='Oakland', spread_one=s1, spread_two=s2,
	         mline_one=m1, mline_two=m2, over=o, under=u)

matchups = get_matchups_sportsbook('https://www.sportsbook.ag/sbk/sportsbook4/baseball-betting/mlb-lines.sbk', 'lxml', 'Baseball')

matchups2 = get_matchups_betus('http://www.betus.com.pa/sportsbook/nfl-football-lines.aspx', 'lxml', 'Football')

matchups3 = get_matchups_bovada('https://sports.bovada.lv/football/nfl/game-lines-market-group', 'lxml', 'Football')
'''