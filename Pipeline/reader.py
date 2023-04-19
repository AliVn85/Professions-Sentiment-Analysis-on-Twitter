# python3 reader.py -d "../database.db" |  python3 spaCy.py | python3 writer.py -d "../database.db"

from optparse import OptionParser
import sqlite3
from cassis import *
import pandas as pd
import os
from emoji import UNICODE_EMOJI

# Preparing the Cassis and its structure TypeSystem
with open('typesystem.xml', 'rb') as f:
	typesystem = load_typesystem(f)
    
with open('xmlts.xml', 'rb') as f:
	cas = load_cas_from_xmi(f, typesystem=typesystem)

Token = typesystem.get_type('Tweet')

parser = OptionParser()
parser.add_option("-d", "--database", dest="dbpath",default="", action="store", type="string",
                  help="The input file", metavar="filename")
args = parser.parse_args()

(options, args) = parser.parse_args()

sqliteConnection = sqlite3.connect(str(options.dbpath))
cursor  = sqliteConnection.cursor()
sqlite_select_Query = "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='Tweets'"
cursor.execute(sqlite_select_Query)
for row in cursor:
	if(row[0]==0):
		raise Exception("Sorry, Path to the desired DB is not correct!")

cursor.execute("SELECT tweet_id, tweet_txt FROM Tweets WHERE id BETWEEN 3000000 AND (SELECT MAX(id) FROM Tweets)") # To avoid catching the "huge input lookup" error from the cas_to_xmi parser, we scraped 1 million entries each time.

hashtags_df = pd.read_sql("SELECT tweet_id, hashtags from Hashtags", sqlite3.connect("../database.db"))
tempCounter = 0
for tweetID, tweetText in cursor:
	tIdStr = str(tweetID)
	try:
		tweetHashtags = hashtags_df.query('tweet_id == '+tIdStr)['hashtags'].item()
		
		if(not isinstance(tweetHashtags, type(None))):
			tweetHashtags=" ".join(tweetHashtags.split())
	except:
		tweetHashtags=""
	# Avoid illegal characters in xml
	newTweetHashtags = ''.join([i for i in tweetHashtags if i.isalpha() or i in UNICODE_EMOJI or i in [' ','.',',',';',':','!','?','(',')','[',']','{','}','-','_','+','=']])
	newTweetTexts = ''.join([i for i in tweetText if i.isalpha() or i in UNICODE_EMOJI or i in [' ','.',',',';',':','!','?','(',')','[',']','{','}','-','_','+','=']])
		
	cas.add(Token(tHashtags=newTweetHashtags, tText=newTweetTexts, tId=tIdStr, begin=0, end=1))
cursor.close()
sqliteConnection.close()
outputed = cas.to_xmi()

print(outputed)

