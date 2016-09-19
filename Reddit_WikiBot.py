import requests
from   bs4 import BeautifulSoup
import praw
import time
import traceback
import obot
import sqlite3

print("Setting up Config")

''' Config '''

sql = sqlite3.connect('commentdata')
cur = sql.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS oldposts(id TEXT)')

SUBREDDIT = 'BotFinalTesting'

WAIT = 15

ERROR_WAIT = 20

DO_SUBMISSIONS = False
DO_COMMENTS = True

MAXPOSTS = 100

CLEANCYCLES = 10

REPLY ='''
##This action was performed by a bot, please contact /u/Superf1cial for bugs
'''

already_done= []

''' Config '''

print('Logging into Reddit')

r = obot.login()

print('Login succesful')


def parse_data(keyword,REPLY):
    keyword = keyword.replace("Wiki!", "")
    url = ('http://overwatch.gamepedia.com/{0}'.format(keyword))
    raw = requests.get(url)
    soup = BeautifulSoup(raw.text, 'html.parser')
    bio = soup.find('table', 'infoboxtable')
    player = {}
    Abilities = []

    for weapon in soup.select('.ability_details'):
        name = weapon.find('span').text
        player[name] = {}

        for div in weapon.select('.infoboxtable td > div'):
            stat  = div.text.strip().encode('utf-8')
            value = div.find_parent('td').find_next('td').text.strip().encode('utf-8')
            player[name][stat] = value
    for k,v in player.items():
        temp = "{}: {}".format(k, v)
        temp = temp.replace("b'","").replace("{","").replace("}","").replace("'","")
        temp = temp.replace("\\xe2\\x9c\\x95","")
        Abilities.append(temp)
        REPLY += "      {}\n".format(temp)
    return REPLY

def scan_reddit():

    keywords= ['Wiki!Genji', 'Wiki!McCree', 'Wiki!Pharah', 'Wiki!Reaper', 'Wiki!Tracer', 'Wiki!Bastion', 'Wiki!Hanzo', 'Wiki!Junkrat',
               'Wiki!Mei', 'Wiki!Torbjörn', 'Wiki!Widowmaker', 'Wiki!D.Va', 'Wiki!Reinhardt', 'Wiki!Roadhog', 'Wiki!Winston', 'Wiki!Zarya',
               'Wiki!Ana', 'Wiki!Lucio', 'Wiki!Mercy', 'Wiki!Symmetra', 'Wiki!Zenyatta','Soldier:_76']

    print('Searching %s.' % SUBREDDIT)
    subreddit = r.get_subreddit(SUBREDDIT)
    posts = []
    posts += list(subreddit.get_comments(limit=MAXPOSTS))
    posts.sort(key=lambda x: x.created_utc)
    print(posts)

    for post in posts:
        pid = post.id

        try:
            pauthor = post.author.name
        except AttributeError:
            continue

        if pauthor.lower() == r.user.name.lower():
            print('Will not reply to myself.')
            continue

        cur.execute('SELECT * FROM oldposts WHERE ID=?', [pid])
        if cur.fetchone():
            continue

        if isinstance(post, praw.objects.Comment):
            pbody = post.body
        else:
            pbody = '%s %s' % (post.title, post.selftext)
        pbody = pbody.lower()

        if not any(key.lower() in pbody for key in keywords):
            continue

        cur.execute('INSERT INTO oldposts VALUES(?)', [pid])
        sql.commit()
        print('Replying to %s by %s' % (pid, pauthor))
        word = next(filter(lambda x: x in post.body, keywords), None)
        COMMENT = parse_data(word, REPLY)
        try:
                post.reply(COMMENT)
        except praw.errors.Forbidden:
            print('403 FORBIDDEN - is the bot banned from {}?'.format(post.subreddit.display_name))

CYCLES = 0
while True:
    try:
        scan_reddit()
    except Exception as e:
        traceback.print_exc()
        print('An error occured, waiting {}'.format(ERROR_WAIT))
        time.sleep(ERROR_WAIT)
    if CYCLES >= CLEANCYCLES:
        print('time to clean up')
        cur.execute('DELETE FROM oldposts WHERE id NOT IN (SELECT id FROM oldposts ORDER BY id DESC LIMIT ?)', [MAXPOSTS *2])
        sql.commit()
        CYCLES = 0
    print('Running again in {} seconds'.format(WAIT))
    time.sleep(WAIT)

