import requests
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

SUBREDDIT = 'competitiveoverwatch'

WAIT = 15

ERROR_WAIT = 20

MAXPOSTS = 100

CLEANCYCLES = 10

REPLY ='''
Hey it seems like you asked a question that should be posted in /r/learnpython insteadt of here.
They are a great active community and always happy to help out, check them out!

Info of the sidebar:
    If you are about to ask a question, please consider r/learnpython. Homework-style questions will be removed, and you'll be encouraged to post there instead.
'''


''' Config '''

print('Logging into Reddit')

r = obot.login()

print('Login succesful')

def scan_reddit():

    keywords= ['Codecademy','learn Python'] #morekeywords to be added, was just too lazy to check for other posts

    print('Searching %s.' % SUBREDDIT)
    subreddit = r.get_subreddit(SUBREDDIT)
    posts = []
    posts += list(subreddit.get_posts(limit=MAXPOSTS))

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

        if not any(key.lower() in pbody for key in keywords):
            continue

        cur.execute('INSERT INTO oldposts VALUES(?)', [pid])
        sql.commit()
        print('Replying to {} by {}'.format(pid, pauthor))
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
