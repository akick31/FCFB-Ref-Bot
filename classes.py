class offense__type(Enum):
	SPREAD = 1
	PRO = 2
	FLEXBONE = 3
	AIR = 4
	PISTOL = 5


class defense__type(Enum):
	THREE_FOUR = 1
	FOUR_THREE = 2
	FIVE_TWO = 3
	FOUR_FOUR = 4
	THREE_THREE_FIVE = 5


class timeout_option(Enum):
	NONE = 1
	REQUESTED = 2
	USED = 3


class quarter_type(Enum):
	NORMAL = 1
	OVERTIME_NORMAL = 2
	OVERTIME_TIME = 3
	END = 4


class time_option(Enum):
	NORMAL = 1
	CHEW = 2
	HURRY = 3
	RUN = 4


class action(Enum):
	COIN = 1
	DEFER = 2
	PLAY = 3
	CONVERSION = 4
	KICKOFF = 5
	OVERTIME = 6
	END = 7


class play(Enum):
	RUN = 1
	PASS = 2
	PUNT = 3
	FIELD_GOAL = 4
	KNEEL = 5
	SPIKE = 6
	PAT = 7
	TWO_POINT = 8
	KICKOFF_NORMAL = 9
	KICKOFF_SQUIB = 10
	KICKOFF_ONSIDE = 11
	DELAY_OF_GAME = 12


class result(Enum):
	GAIN = 1
	TURNOVER = 2
	TOUCHDOWN = 3
	TURNOVER_TOUCHDOWN = 4
	INCOMPLETE = 5
	TOUCHBACK = 6
	FIELD_GOAL = 7
	MISS = 8
	PAT = 9
	TWO_POINT = 10
	KICKOFF = 11
	PUNT = 12
	KICK = 13
	SPIKE = 14
	KNEEL = 15
	SAFETY = 16
	ERROR = 17
	TURNOVER_PAT = 18
	END_HALF = 19
	DELAY_OF_GAME = 20
    
class home_away:
	def __init__(self, isHome):
		self.isHome = isHome

	def set(self, isHome):
		self.isHome = isHome

	def name(self):
		if self.isHome:
			return "home"
		else:
			return "away"

	def negate(self):
		return home_away(not self.isHome)

	def reverse(self):
		current = self.isHome
		reversed = not current
		self.isHome = reversed

	def copy(self):
		return home_away(self.isHome)

	def __eq__(self, value):
		if isinstance(value, bool):
			return self.isHome == value
		elif isinstance(value, str):
			return self.name() == value
		elif isinstance(value, home_away):
			return self.isHome == value.isHome
		else:
			return NotImplemented

	def __bool__(self):
		return self.isHome

	def __str__(self):
		return self.name()
    
class team_state:
	def __init__(self):
		self.points = 0
		self.quarters = [0, 0, 0, 0]

		self.playclockPenalties = 0
		self.timeouts = 3
		self.requestedTimeout = timeout_option.NONE


class team_stats:
	def __init__(self):
		self.yardsPassing = 0
		self.yardsRushing = 0
		self.yardsTotal = 0
		self.turnoverInterceptions = 0
		self.turnoverFumble = 0
		self.fieldGoalsScored = 0
		self.fieldGoalsAttempted = 0
		self.posTime = 0
        
class playbook:
	def __init__(self, offense=None, defence=None):
		self.offense = offense
		self.defense = defence


class game_status:
	def __init__(self, quarterLength):
		self.clock = quarterLength
		self.quarter = 1
		self.location = -1
		self.possession = home_away(T.home)
		self.down = 1
		self.yards = 10
		self.quarterType = quarter_type.NORMAL
		self.overtimePossession = None
		self.receivingNext = home_away(T.home)
		self.homeState = team_state()
		self.awayState = team_state()
		self.homeStats = team_stats()
		self.awayStats = team_stats()
		self.waitingId = ""
		self.waitingAction = action.COIN
		self.waitingOn = home_away(T.away)
		self.defensiveNumber = None
		self.defensiveSubmitter = None
		self.messageId = None
		self.winner = None
		self.timeRunoff = False
		self.plays = [[]]
		self.drives = []
		self.noOnside = False

		self.homePlaybook = Playbook()
		self.awayPlaybook = Playbook()

	def state(self, isHome):
		if isHome:
			return self.homeState
		else:
			return self.awayState

	def stats(self, isHome):
		if isHome:
			return self.homeStats
		else:
			return self.awayStats

	def playbook(self, isHome):
		if isHome:
			return self.homePlaybook
		else:
			return self.awayPlaybook

	def reset_defensive(self):
		self.defensiveNumber = None
		self.defensiveSubmitter = None


class team:
	def __init__(self, tag, name, offense, defense, conference=None, css_tag=None):
		self.tag = tag
		self.name = name
		self.playbook = Playbook(offense, defense)
		self.coaches = []
		self.pastCoaches = []
		self.record = None
		self.conference = conference
		self.css_tag = css_tag


class game:
	def __init__(self, home, away, quarterLength=None):
		self.home = home
		self.away = away

		self.dirty = False
		self.errored = False
		self.thread = "empty"
		self.previousStatus = []
		self.startTime = None
		self.location = None
		self.station = None
		self.prefix = None
		self.suffix = None
		self.playclock = datetime.utcnow() + timedelta(hours=24)
		self.deadline = datetime.utcnow() + timedelta(days=10)
		self.forceChew = False
		self.playclockWarning = False
		self.playGist = None
		self.playRerun = False
		if quarterLength is None:
			self.quarterLength = 7*60
		else:
			self.quarterLength = quarterLength
		self.status = GameStatus(self.quarterLength)

	def team(self, isHome):
		if isHome:
			return self.home
		else:
			return self.away

	def __str__(self):
		return self.__dict__


movementPlays = [Play.RUN, Play.PASS]
normalPlays = [Play.RUN, Play.PASS, Play.PUNT, Play.FIELD_GOAL]
timePlays = [Play.KNEEL, Play.SPIKE]
conversionPlays = [Play.PAT, Play.TWO_POINT]
kickoffPlays = [Play.KICKOFF_NORMAL, Play.KICKOFF_SQUIB, Play.KICKOFF_ONSIDE]
playActions = [Action.PLAY, Action.CONVERSION, Action.KICKOFF]

driveEnders = [Result.TURNOVER, Result.FIELD_GOAL, Result.PUNT, Result.MISS, Result.SAFETY]
scoringResults = [Result.TOUCHDOWN, Result.TURNOVER_TOUCHDOWN]
postTouchdownEnders = [Result.PAT, Result.TWO_POINT, Result.KICKOFF, Result.TURNOVER_PAT]
