NEEDED_FIELDS = ['team_one', 'team_two', 'spread_one', 'spread_two', 'mline_one', 'mline_two', 'over', 'under']
SPECIAL_VALUES = ['even', 'pk', '-', ' ', ' -', '']
NAME_TABLE_NFL = {
		'KC': 	'Kansas City Chiefs',
		'NE': 	'New England Patriots',
		'NYJ': 	'New York Jets',
		'BUF':	'Buffalo Bills',
		'ATL':	'Atlanta Falcons',
		'CHI': 	'Chicago Bears',
		'PHI':	'Philadelphia Eagles',
		'WAS':	'Washington Redskins',
		'PIT':	'Pittsburgh Steelers',
		'CLE':	'Cleveland Browns',
		'BAL':	'Baltimore Ravens',
		'CIN':	'Cincinnati Bengals',
		'ARI':	'Arizona Cardinals',
		'DET':	'Detroit Lions',
		'TB':	'Tampa Bay Buccaneers',
		'MIA':	'Miami Dolphins',
		'OAK':	'Oakland Raiders',
		'TEN':	'Tennessee Titans',
		'JAX':	'Jacksonville Jaguars',
		'HOU': 	'Houston Texans',
		'IND':	'Indianapolis Colts',
		'LA':	'LA Rams',
		'SEA':	'Seattle Seahawks',
		'GB':	'Green Bay Packers',
		'CAR':	'Carolina Panthers',
		'SF': 	'San Francisco 49ers',
		'NYG':	'New York Giants',
		'DAL':	'Dallas Cowboys',
		'NO':	'New Orleans Saints',
		'MIN':	'Minnesota Vikings',
}

WEBSITES = {}
WEBSITES['bovada'] = {}
WEBSITES['betus'] = {}
WEBSITES['sportsbook'] = {}

WEBSITES['bovada']['nfl'] = 'https://sports.bovada.lv/football/nfl/game-lines-market-group'
WEBSITES['bovada']['nba'] = 'https://sports.bovada.lv/baketball/nba/game-lines-market-group'

WEBSITES['betus']['nba'] = 'http://www.betus.com.pa/sportsbook/nba-basketball-lines.aspx'
WEBSITES['betus']['nfl'] = 'http://www.betus.com.pa/sportsbook/nfl-football-lines.aspx' 

WEBSITES['sportsbook']['mlb'] = 'https://www.sportsbook.ag/sbk/sportsbook4/baseball-betting/mlb-lines.sbk'
WEBSITES['sportsbook']['nba'] = 'https://www.sportsbook.ag/sbk/sportsbook4/nba-finals-betting/game-lines.sbk'
WEBSITES['sportsbook']['nfl'] = 'https://www.sportsbook.ag/sbk/sportsbook4/nfl-betting/game-lines.sbk'
WEBSITES['sportsbook']['ncaaf'] = 'https://www.sportsbook.ag/sbk/sportsbook4/ncaa-football-betting/game-lines.sbk'



class Line(object):
	def __init__(self, kind, value, odds=''):
		self.kind = kind
		self.value = value
		self.odds = odds.lower()

	def __repr__(self):
		s = ''
		if self.kind == 'O' or self.kind == 'U':
			s += self.kind + ' '

		s += self.value

		if self.odds != '':
			s += '(' + self.odds + ')'

		return s

	def get_numerical_value(self):
		if self.value in SPECIAL_VALUES:
			return 0.0
		else:
			return float(self.value)

	def get_numerical_odds(self):
		if self.odds in SPECIAL_VALUES:
			return 100.0
		else:
			return float(self.odds)


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

		if sport == 'nfl':
			for key, value in NAME_TABLE_NFL.items():
				if self.team_one == key:
					self.team_one = NAME_TABLE_NFL[self.team_one]
				if self.team_two == key:
					self.team_two = NAME_TABLE_NFL[self.team_two]

	def __repr__(self):
		line_one = self.team_one + '  '
		line_two = self.team_two + '  '

		diff = len(self.team_one) - len(self.team_two)

		if diff > 0:
			line_two += ' ' * diff
		if diff < 0:
			diff *= -1
			line_one += ' ' * diff 

		line_one += '  '.join([str(self.spread_one), str(self.mline_one), str( self.over)])
		line_two += '  '.join([str(self.spread_two), str(self.mline_two), str(self.under)])

		return self.website + '\n' + line_one + '\n' + line_two + '\n'

