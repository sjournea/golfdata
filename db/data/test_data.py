import datetime
from .test_courses import *

GolfPlayers = (
  {'email':'sjournea@tl.com', 'first_name': 'Steve', 'last_name': 'Journeay', 'nick_name': 'Hammy',  'handicap': 18.4, 'gender': 'man', 'id': 1},
  {'email':'snake@tl.com',    'first_name': 'Chris', 'last_name': 'Jensen',   'nick_name': 'Snake',  'handicap': 18.0, 'gender': 'man', 'id': 2},
  {'email':'spanky@tl.com',   'first_name': 'Rob',   'last_name': 'Sullivan', 'nick_name': 'Spanky', 'handicap': 16.3, 'gender': 'man', 'id': 3},
  {'email':'reload@tl.com',   'first_name': 'Mike',  'last_name': 'Davis',    'nick_name': 'Reload', 'handicap': 20.5, 'gender': 'man', 'id': 4},
  {'email':'bomba@tl.com',    'first_name': 'Rhonda','last_name': 'Journeay', 'nick_name': 'Bomba',  'handicap': 31.8, 'gender': 'woman', 'id': 5},
  {'email':'ruby@tl.com',     'first_name': 'Ruby',  'last_name': 'Journeay', 'nick_name': 'Frenchie', 'handicap': 11.2, 'gender': 'woman', 'id': 6},
  {'email':'perl@tl.com',     'first_name': 'Perl',  'last_name': 'Journeay', 'nick_name': 'Cattle', 'handicap': 8.6, 'gender': 'woman', 'id': 7},
)

TestGolfPlayers = [
  {'email':'jlennon@beatles.com',   'first_name': 'John',   'last_name': 'Lennon',    'nick_name': 'JL', 'handicap': 15, 'gender': 'man'},
  {'email':'pmccartn@beatles.com',  'first_name': 'Paul',   'last_name': 'McCartney', 'nick_name': 'PM', 'handicap': 15, 'gender': 'man'},
  {'email':'gharriso@beatles.com',  'first_name': 'George', 'last_name': 'Harrison',  'nick_name': 'GH', 'handicap': 15, 'gender': 'man'},
  {'email':'rstarr@beatles.com',    'first_name': 'Ringo',  'last_name': 'Starr',     'nick_name': 'RS', 'handicap': 15, 'gender': 'man'},
]

CanyonLake_Players = [
  {'player': GolfPlayers[0], 'tee':canyon_lake_tees[0],
   'gross': { 'score': [4,8,5,11,4,7,7,5,6, 6,4,7,5,10,4,6,8,5]}},
  {'player': GolfPlayers[1], 'gross': [5,8,7,4,4,6,6,5,7,  4,4,7,6,6,5,6,7,8], 'tee':canyon_lake_tees[0]},
  {'player': GolfPlayers[2], 'gross': [6,7,4,7,3,4,7,6,5,  5,5,7,4,6,4,6,6,6], 'tee':canyon_lake_tees[0]},
  {'player': GolfPlayers[3], 'gross': [7,8,7,7,7,6,8,7,6,  5,7,7,5,8,5,6,7,7], 'tee':canyon_lake_tees[0]},
]

LakeChabot_Players = [
  {'player': GolfPlayers[0], 'gross': [5,6,6,6,6,5,4,5,5, 6,6,3,8,5,3,6,4,7], 'tee':lake_chabot_tees[0]},
  {'player': GolfPlayers[1], 'gross': [6,4,6,7,5,5,4,5,4, 6,5,4,5,6,5,6,4,7], 'tee':lake_chabot_tees[0]},
  {'player': GolfPlayers[2], 'gross': [6,4,7,5,4,4,5,6,3, 5,5,4,6,5,7,8,4,5], 'tee':lake_chabot_tees[0]},
  {'player': GolfPlayers[3], 'gross': [5,6,7,6,5,6,3,6,6, 6,6,7,6,8,6,7,5,6], 'tee':lake_chabot_tees[0]},
]

DeltaView_Players = [
  {'player': GolfPlayers[0], 'gross': [7,7,4,6,6,4,6,5,6, 6,8,7,4,6,5,5,6,8], 'tee': delta_view_tees[0]},
  {'player': GolfPlayers[1], 'gross': [6,7,4,5,8,3,5,4,6, 6,5,6,4,6,6,6,5,6], 'tee': delta_view_tees[0]},
  {'player': GolfPlayers[2], 'gross': [6,7,5,3,5,3,8,6,6, 6,6,5,5,5,3,5,7,5], 'tee': delta_view_tees[0]},
]

Skywest_Players = [
  {'player': GolfPlayers[0], 'gross': [7,4,6,7,4,5,6,4,5, 5,5,5,5,6,4,4,5,5], 'tee': skywest_tees[0]},
  {'player': GolfPlayers[1], 'gross': [6,7,4,6,4,7,5,3,6, 5,4,3,7,6,5,4,6,4], 'tee': skywest_tees[0]},
  {'player': GolfPlayers[2], 'gross': [7,6,5,7,4,5,5,3,5, 6,5,4,5,5,5,4,6,5], 'tee': skywest_tees[0]},
  {'player': GolfPlayers[3], 'gross': [8,5,7,6,5,6,5,5,6, 4,7,4,7,7,5,5,6,7], 'tee': skywest_tees[0]},
]

GolfRounds = [
  { 'date': datetime.datetime(2017, 3, 7), 
    'course': GolfCourses[0],
    'players': CanyonLake_Players,
    'tee': GolfCourses[0]['tees'][0],
  },
  { 'date': datetime.datetime(2016, 6, 8), 
    'course': GolfCourses[4],
    'players': LakeChabot_Players,
    'tee': GolfCourses[4]['tees'][0],
  },
  { 'date': datetime.datetime(2016, 10, 1), 
    'course': GolfCourses[5],
    'players': DeltaView_Players,
    'tee': GolfCourses[5]['tees'][0],
  },
]

DBGolfRounds = [
  { 'date': datetime.datetime(2017, 3, 7), 
    'course': GolfCourses[0],
    'players': CanyonLake_Players,
    'tee': GolfCourses[0]['tees'][0],
  },
  { 'date': datetime.datetime(2016, 6, 8), 
    'course': GolfCourses[4],
    'players': LakeChabot_Players,
    'tee': GolfCourses[4]['tees'][0],
  },
  { 'date': datetime.datetime(2016, 10, 1), 
    'course': GolfCourses[5],
    'players': DeltaView_Players,
    'tee': GolfCourses[5]['tees'][0],
  },
]

Canyon_Lakes_2017_03_04 = {
  'course': 'Canyon',
  'date' : '2017-03-04',
  'players': (
      ('sjournea', 'Blue'),
      ('snake', 'Blue'),
      ('spanky', 'Blue'),
      ('reload', 'Blue'),
  ),
  'scores': (
    (1, (4, 5, 6, 5)),
    (2, (8, 6, 5, 8)),
    (3, (3, 4, 6, 4)),
    (4, (6, 5, 6, 7)),
    (5, (3, 5, 4, 4)),
    (6, (5, 4, 4, 4)),
    (7, (5, 6, 6, 7)),
    (8, (6, 5, 4, 6)),
    (9, (6, 5, 6, 7)),
    (10, (5, 3, 3, 4)),
    (11, (4, 4, 5, 6)),
    (12, (6, 4, 3, 6)),
    (13, (4, 3, 3, 4)),
    (14, (8, 5, 6, 8)),
    (15, (4, 4, 4, 4)),
    (16, (6, 5, 5, 6)),
    (17, (7, 6, 6, 6)),
    (18, (4, 6, 5, 6)),
  )
}

Delta_2016_10_01 = {
  'course': 'Delta',
  'date' : '2016-10-01',
  'players': (
      ('sjournea', 'Blue'),
      ('snake', 'Blue'),
      ('spanky', 'Blue'),
  ),
  'scores': (
    (1, (7,6,6)),
    (2, (7,7,7)),
    (3, (4,4,5)),
    (4, (6,5,3)),
    (5, (6,8,5)),
    (6, (4,3,3)),
    (7, (6,5,8)),
    (8, (5,4,6)),
    (9, (6,6,6)),
    (10, (6,6,6)),
    (11, (8,5,6)),
    (12, (7,6,5)),
    (13, (4,4,5)),
    (14, (6,6,5)),
    (15, (5,6,3)),
    (16, (5,6,5)),
    (17, (6,5,7)),
    (18, (8,6,5)),
  )
}

Monarch_2017_04_01 = {
  'course': 'Monarch',
  'date' : '2017-04-01',
  'players': (
      ('sjournea', 'Tournament'),
      ('snake', 'Tournament'),
      ('spanky', 'Tournament'),
      ('reload', 'Tournament'),
  ),
  'scores': (
    (1, (5,7,5,4)),
    (2, (6,6,6,5)),
    (3, (5,5,8,5)),
    (4, (4,4,4,4)),
    (5, (6,7,5,7)),
    (6, (7,6,6,6)),
    (7, (4,4,7,5)),
    (8, (9,5,6,5)),
    (9, (5,5,5,5)),
    (10, (3,5,2,5)),
    (11, (5,6,5,5)),
    (12, (9,8,9,8)),
    (13, (7,5,6,6)),
    (14, (4,5,5,5)),
    (15, (6,5,5,5)),
    (16, (8,7,7,7)),
    (17, (4,4,4,5)),
    (18, (8,7,5,5)),
   )
}

Chabot_2016_06_08 = {
  'course': 'Chabot',
  'date' : '2016-06-08',
  'players': (
    ('sjournea', 'Blue'),
    ('snake', 'Blue'),
    ('spanky', 'Blue'),
    ('reload', 'Blue'),
  ),
  'scores': (
    (1, (5,6,6,5)),
    (2, (6,4,4,6)),
    (3, (6,6,7,7)),
    (4, (6,7,5,6)),
    (5, (6,5,4,5)),
    (6, (5,5,4,6)),
    (7, (4,4,5,3)),
    (8, (5,5,6,6)),
    (9, (5,4,3,6)),
    (10, (6,6,5,6)),
    (11, (6,5,5,6)),
    (12, (3,4,4,7)),
    (13, (8,5,6,6)),
    (14, (5,6,5,8)),
    (15, (3,5,7,6)),
    (16, (6,6,8,7)),
    (17, (4,4,4,5)),
    (18, (7,7,5,6)),
  )
}

RoundsPlayed = [
  Chabot_2016_06_08,
  Delta_2016_10_01,
  Canyon_Lakes_2017_03_04,
  Monarch_2017_04_01,
]