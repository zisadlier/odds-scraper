NEEDED_FIELDS = ['team_one', 'team_two', 'spread_one', 'spread_two', 'mline_one', 'mline_two', 'over', 'under']
SPECIAL_VALUES = ['even', 'pk', '-', ' ', ' -', '', 'pick']
NAME_TABLE_NFL = {
		'KC': 	'Kansas City Chiefs',
		'KANSAS CITY': 	'Kansas City Chiefs',
		'NE': 	'New England Patriots',
		'NEW ENGLAND': 	'New England Patriots',
		'NYJ': 	'New York Jets',
		'NY JETS': 	'New York Jets',
		'BUF':	'Buffalo Bills',
		'BUFFALO':	'Buffalo Bills',
		'ATL':	'Atlanta Falcons',
		'ATLANTA':	'Atlanta Falcons',
		'CHI': 	'Chicago Bears',
		'CHICAGO': 	'Chicago Bears',
		'PHI':	'Philadelphia Eagles',
		'PHILADELPHIA':	'Philadelphia Eagles',
		'WAS':	'Washington Redskins',
		'WASHINGTON':	'Washington Redskins',
		'PIT':	'Pittsburgh Steelers',
		'PITTSBURGH':	'Pittsburgh Steelers',
		'CLE':	'Cleveland Browns',
		'CLEVELAND':	'Cleveland Browns',
		'BAL':	'Baltimore Ravens',
		'BALTIMORE':	'Baltimore Ravens',
		'CIN':	'Cincinnati Bengals',
		'CINCINNATI':	'Cincinnati Bengals',
		'ARI':	'Arizona Cardinals',
		'ARIZONA':	'Arizona Cardinals',
		'DET':	'Detroit Lions',
		'DETROIT':	'Detroit Lions',
		'TB':	'Tampa Bay Buccaneers',
		'TAMPA BAY':	'Tampa Bay Buccaneers',
		'MIA':	'Miami Dolphins',
		'MIAMI':	'Miami Dolphins',
		'OAK':	'Oakland Raiders',
		'OAKLAND':	'Oakland Raiders',
		'TEN':	'Tennessee Titans',
		'TENNESSEE':	'Tennessee Titans',
		'JAX':	'Jacksonville Jaguars',
		'JACKSONVILLE':	'Jacksonville Jaguars',
		'HOU': 	'Houston Texans',
		'HOUSTON': 	'Houston Texans',
		'IND':	'Indianapolis Colts',
		'INDIANAPOLIS':	'Indianapolis Colts',
		'LA':	'LA Rams',
		'LA RAMS':	'LA Rams',
		'LAR': 'LA Rams',
		'LAC':	'LA Chargers',
		'LA CHARGERS':	'LA Chargers',
		'Los Angeles Rams':	'LA Rams',
		'Los Angeles Chargers': 'LA Chargers',
		'DEN':	'Denver Broncos',
		'DENVER':	'Denver Broncos',
		'SEA':	'Seattle Seahawks',
		'SEATTLE':	'Seattle Seahawks',
		'GB':	'Green Bay Packers',
		'GREEN BAY':	'Green Bay Packers',
		'CAR':	'Carolina Panthers',
		'CAROLINA':	'Carolina Panthers',
		'SF': 	'San Francisco 49ers',
		'SAN FRANCISCO': 	'San Francisco 49ers',
		'NYG':	'New York Giants',
		'NY GIANTS':	'New York Giants',
		'DAL':	'Dallas Cowboys',
		'DALLAS':	'Dallas Cowboys',
		'NO':	'New Orleans Saints',
		'NEW ORLEANS':	'New Orleans Saints',
		'MIN':	'Minnesota Vikings',
		'MINNESOTA':	'Minnesota Vikings',
}

SB_HTML_TOOLS = {}
SB_HTML_TOOLS['nfl'] = ["img[src*='football']", "//a[text()='NFL']"]
SB_HTML_TOOLS['ncaaf'] = ["img[src*='football']", "//a[text()='NCAA']"]

WEBSITES = {}
WEBSITES['bovada'] = {}
WEBSITES['betus'] = {}
WEBSITES['sportsbook'] = {}
WEBSITES['sportsbetting'] = {}
WEBSITES['betlucky'] = {}
WEBSITES['gtbets'] = {}

WEBSITES['bovada']['nfl'] = 'https://sports.bovada.lv/football/nfl/game-lines-market-group'
WEBSITES['bovada']['nba'] = 'https://sports.bovada.lv/baketball/nba/game-lines-market-group'

WEBSITES['betus']['nba'] = 'http://www.betus.com.pa/sportsbook/nba-basketball-lines.aspx'
WEBSITES['betus']['nfl'] = 'http://www.betus.com.pa/sportsbook/nfl-football-lines.aspx' 

#WEBSITES['sportsbook']['mlb'] = 'https://www.sportsbook.ag/sbk/sportsbook4/baseball-betting/mlb-lines.sbk'
WEBSITES['sportsbook']['nba'] = 'https://www.sportsbook.ag/sbk/sportsbook4/nba-finals-betting/game-lines.sbk'
WEBSITES['sportsbook']['nfl'] = 'https://www.sportsbook.ag/sbk/sportsbook4/nfl-betting/game-lines.sbk'
WEBSITES['sportsbook']['ncaaf'] = 'https://www.sportsbook.ag/sbk/sportsbook4/ncaa-football-betting/game-lines.sbk'

WEBSITES['sportsbetting']['nfl'] = 'https://www.sportsbetting.ag/sportsbook'
WEBSITES['sportsbetting']['ncaaf'] = 'https://www.sportsbetting.ag/sportsbook'
WEBSITES['sportsbetting']['nba'] = 'https://www.sportsbetting.ag/sportsbook'

WEBSITES['betlucky']['nfl'] = 'http://betluckys.ag/sports?curOption=FOOTBALL/*/NFL/*/'

WEBSITES['gtbets']['nfl'] = 'https://www.gtbets.eu/wagering1.asp?mode=lines&league=NFL&lg=1'
WEBSITES['gtbets']['ncaaf'] = 'https://www.gtbets.eu/wagering1.asp?mode=lines&league=CF&lg=1'

COLORS = {
	'red': '\033[0;31m',
	'green': '\033[0;32m',
	'yellow': '\033[0;33m',
	'cyan': '\033[0;36m',
}

class Line(object):
	def __init__(self, kind, value, odds=''):
		self.kind = kind
		self.value = value
		self.odds = odds

		# Insert a '+'' if the value is positive but does not already have a '+'
		if isinstance(self.value, str) and self.value.lower() not in SPECIAL_VALUES:
			if sign(float(self.value)) == 1 and self.value[0] != '+':
				self.value = '+' + self.value

		if not isinstance(self.value, str):
			pos = ''
			if sign(self.value) == 1:
				pos = '+'

			if self.value.is_integer():
				self.value = str(self.value)

			self.value = pos + str(self.value)

		if not isinstance(self.odds, str):
			pos = ''
			if sign(self.odds) == 1:
				pos = '+'

			if self.odds.is_integer():
				self.odds = int(self.odds)

			self.odds = pos + str(self.odds)

	def __repr__(self):
		s = ''
		if self.kind == 'O' or self.kind == 'U':
			s += self.kind + ' '

		s += self.value

		if self.odds != '':
			s += '(' + self.odds + ')'

		return s

	def get_numerical_value(self):
		if self.value.lower() in SPECIAL_VALUES:
			return 0.0
		else:
			return float(self.value)

	def get_numerical_odds(self):
		if self.odds.lower() in SPECIAL_VALUES:
			return 100.0
		else:
			return float(self.odds)

	def get_string(self):
		if self.odds != '':
			if self.value == '+0.0':
				self.value = 'Even'
			return self.value + ' ' + '(' + self.odds + ')'
		if self.odds == '' and self.value == '+0.0':
			return '-'
		if self.odds == '':
			return self.value


class Matchup(object):
	def __init__(self, sport, website, **kwargs):
		for field in NEEDED_FIELDS:
			if field not in kwargs:
				raise Exception('Missing needed field for matchup setup: ', field)

		self.sport = sport
		self.website = website
		self.team_one = kwargs['team_one']
		self.team_two = kwargs['team_two']
		self.mline_one = kwargs['mline_one']
		self.mline_two = kwargs['mline_two']
		self.spread_one = kwargs['spread_one']
		self.spread_two = kwargs['spread_two']
		self.over = kwargs['over']
		self.under = kwargs['under']
		self.offset = ''

		if sport == 'nfl':
			for key, value in NAME_TABLE_NFL.items():
				if self.team_one == key:
					self.team_one = NAME_TABLE_NFL[self.team_one]
				if self.team_two == key:
					self.team_two = NAME_TABLE_NFL[self.team_two]

	def __repr__(self):
		l1 = [self.team_one, str(self.spread_one), str(self.mline_one), str(self.over)]
		l2 = [self.team_two, str(self.spread_two), str(self.mline_two), str(self.under)]

		line_one = ''
		line_two = ''

		for i in range(0, 4):
			elt_one = l1[i]
			elt_two = l2[i]

			diff = len(elt_one) - len(elt_two)

			if diff > 0:
				elt_two += ' ' * diff
			if diff < 0:
				diff *= -1
				elt_one += ' ' * diff 

			line_one += elt_one + '  '
			line_two += elt_two + '  '

			if i == 0 and self.offset != '':
				line_one += self.offset
				line_two += self.offset

		return self.website + '\n' + line_one + '\n' + line_two + '\n'

	def get_key(self):
		ls = sorted([self.team_one, self.team_two], key=lambda s: str.lower(s))
		try:
			key = ls[0][:3] + ls[1][:3]
		except IndexError as ie:
			raise ie

		return key

	def add_website(self, website):
		self.website += (', ' + website)

def sign(num):
	if num < 0:
		return -1
	return 1

def add_color(string, color):
	if color not in COLORS.keys():
		raise Exception("Invalid color")

	color_code = COLORS[color]
	no_color = '\033[0m'

	return color_code + string + no_color

def add_spreads(spread_one, spread_two, decimal):
	
	val = spread_one[0] + spread_two[0]

	val /= 2

	odds = None

	if sign(spread_one[1]) == sign(spread_two[1]):
		odds = (spread_one[1] + spread_two[1])/2
		return [float(decimal.format(val)), float(decimal.format(odds))]

	if abs(spread_one[1]) == abs(spread_two[1]):
		odds = 100.0
		return [float(decimal.format(val)), float(decimal.format(odds))]

	higher = max(abs(spread_one[1]), abs(spread_two[1]))

	odds = ((abs(spread_one[1] + spread_two[1]) + 200) * sign(higher))/2
	return [float(decimal.format(val)), float(decimal.format(odds))]

def add_mlines(mline_one, mline_two, decimal):
	odds = None

	if mline_one[0] == 0:
		odds = mline_two[0]
		return [float(decimal.format(odds)), 100.0]
	if mline_two[0] == 0:
		odds = mline_one[0]
		return [float(decimal.format(odds)), 100.0]

	if sign(mline_one[0]) == sign(mline_two[0]):
		odds = (mline_one[0] + mline_two[0])/2
		return [float(decimal.format(odds)), 100.0]

	if abs(mline_one[0]) == abs(mline_two[0]):
		return [float(decimal.format(odds)), 100.0]

	higher = max(abs(mline_one[0]), abs(mline_two[0]))

	odds = ((abs(mline_one[0] + mline_two[0]) + 200) * sign(higher))/2
	return [float(decimal.format(odds)), 100.0]