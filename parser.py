import urllib2
import json
import MySQLdb

db = MySQLdb.connect(host="localhost", user="root", passwd="11111", db="steamparser", charset='utf8')
cursor = db.cursor()

def fill_games():
  url = "http://api.steampowered.com/ISteamApps/GetAppList/v2?key=67E929AA374B527BD8EF8B073F61DC41"
  loaded_json = json.loads(urllib2.urlopen(url).read())
  for app in loaded_json["applist"]["apps"]:
    query = "insert ignore into steamparser.games (gameid, gamename) values ({0}, '{1}');".format(app["appid"], app["name"].encode('utf-8').replace("'", "''"))
    cursor.execute(query)
    db.commit()

def fill_user_friends(steamid):
  url = "http://api.steampowered.com/ISteamUser/GetFriendList/v1/?key=67E929AA374B527BD8EF8B073F61DC41&steamid={0}&format=json".format(steamid)
  try:
    loaded_json = json.loads(urllib2.urlopen(url).read())
  except (urllib2.HTTPError):
    return
  for friend in loaded_json["friendslist"]["friends"]:
    query = "insert ignore into steamparser.users (steamid) values ({0});".format(friend["steamid"])
    cursor.execute(query)
    db.commit()

def fill_user_processing_date(steamid):
  query = "update steamparser.users set processingDate = curdate() where steamid = {0}".format(steamid)
  cursor.execute(query)
  db.commit()

def get_user_to_process():
  query = "select steamid from steamparser.users order by processingDate limit 0,1"
  user_cursor = db.cursor()
  user_cursor.execute(query)
  result = user_cursor.fetchone()[0]
  user_cursor.close()
  return result

def clear_user_games(steamid):
  query = "delete from  steamparser.usergames where usersteamid = {0}".format(steamid)
  cursor.execute(query)
  db.commit()

def insert_user_games(steamid):
  url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=67E929AA374B527BD8EF8B073F61DC41&steamid={0}&format=json".format(steamid)
  loaded_json = json.loads(urllib2.urlopen(url).read())
  if "games" in loaded_json["response"]:
    unsorted_games = loaded_json["response"]["games"]
    sorted_games = sorted(unsorted_games, key=lambda k: k['playtime_forever'], reverse=True)
    position = 1
    for game in sorted_games[:5]:
      query = "insert into steamparser.usergames (usersteamid, gamesteamid, position) values ({0}, {1}, {2});".format(steamid, game["appid"], position)
      cursor.execute(query)
      db.commit()
      position += 1


def update_user_games(steamid):
  clear_user_games(steamid)
  insert_user_games(steamid)

fill_games()
counter = 0

while counter < 50000:
  counter += 1
  userid = get_user_to_process()
  fill_user_friends(userid)
  update_user_games(userid)
  fill_user_processing_date(userid)

db.close()
