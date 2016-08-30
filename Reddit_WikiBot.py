import requests
from   bs4 import BeautifulSoup
import praw
import time
import traceback
import obot

print("Setting up Config")

''' Config '''

SUBREDDIT = 'PythonWikiBotTesting'

MAXPOSTS = 60

WAIT = 30

ERROR_WAIT = 20

''' ALL DONE '''

print('Logging into Reddit')

r = praw.Reddit(obot.app_us)
r.set_oauth_app_info(obot.app_id,obot.app_secret,obot.app_uri)
r.refresh_access_information(obot.app_refresh)
print('Login succesful')


def parse_data(keyword):
    keyword = keyword.replace("Wiki!", "")
    url = ('http://overwatch.gamepedia.com/{0}'.format(keyword))
    raw = requests.get(url)
    soup = BeautifulSoup(raw.text, 'html.parser')
    bio = soup.find('table', 'infoboxtable')
    player = {}

    for weapon in soup.select('.ability_details'):
        name = weapon.find('span').text
        player[name] = {}

        for div in weapon.select('.infoboxtable td > div'):
            stat  = div.text.strip().encode('utf-8')
            value = div.find_parent('td').find_next('td').text.strip().encode('utf-8')
            player[name][stat] = value

    playerlist = []

    for key, value in player.items():
        temp = [key,value]
        playerlist.append(temp)
    return playerlist

def scan_reddit():

    already_done = []
    keywords= ['Wiki!Genji', 'Wiki!McCree', 'Wiki!Pharah', 'Wiki!Reaper', 'Wiki!Tracer', 'Wiki!Bastion', 'Wiki!Hanzo', 'Wiki!Junkrat',
               'Wiki!Mei', 'Wiki!Torbjörn', 'Wiki!Widowmaker', 'Wiki!D.Va', 'Wiki!Reinhardt', 'Wiki!Roadhog', 'Wiki!Winston', 'Wiki!Zarya',
               'Wiki!Ana', 'Wiki!Lucio', 'Wiki!Mercy', 'Wiki!Symettra', 'Wiki!Zenyatta']

    reddit = r.get_subreddit(SUBREDDIT)
    for c in praw.helpers.comment_stream(r,reddit,limit=None):
        has_word = any(string in c.body for string in keywords)
        if c.id not in already_done and has_word:
            author = c.author
            word = next(filter(lambda x: x in c.body, keywords), None)
            data = parse_data(word)
            print('Replying to {}s comment'.format(author))
            c.reply('''
I'm just a bot, please hate my developer /u/Superf1cial.

**Abilities**

        {}

        {}

        {}

        {}

        {}

Please don't abuse me, I have feelings.
            '''.format(data[0], data[1],data[2],data[3], data[4]))
            already_done.append(c.id)

while True:
    try:
        scan_reddit()
    except Exception as e:
        traceback.print_exc()
        print('An error occured, waiting {}'.format(ERROR_WAIT))
        time.sleep(ERROR_WAIT)
    print('Running again in {} seconds'.format(WAIT))
    time.sleep(WAIT)
