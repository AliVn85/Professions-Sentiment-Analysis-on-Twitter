import sqlite3
from sqlite3 import Error
import ast
import sys
from optparse import OptionParser
from cassis import *

# Preparing the Cassis and its structure TypeSystem
with open('typesystem.xml', 'rb') as f:
    typesystem = load_typesystem(f)

lines = ""
for line in sys.stdin:
    lines=lines+line

cas = load_cas_from_xmi(str(lines),typesystem=typesystem)
tweets = cas.select('Tweet')

###########################

parser = OptionParser() # Use -o or -overwrite to overwrite the database changes entirely based on the new input only, else it will add to the database additively.
parser.add_option("-d", "--database", dest="dbpath", default="", action="store", type="string", help="The input file", metavar="filename")
parser.add_option("-o", "--overwrite", action="store_true", dest="dboverwrite", default=False, help="Overwrite the table of Sentiments")
args = parser.parse_args()
(options, args) = parser.parse_args()

sqliteConnection = sqlite3.connect(str(options.dbpath))
cursor = sqliteConnection.cursor()
sqlite_select_Query = "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='Tweets'"
cursor.execute(sqlite_select_Query)
for row in cursor:
	if(row[0]==0):
		raise Exception("Sorry, Path to the desired DB is not correct!")
if (options.dboverwrite):
	cursor.execute('DROP TABLE IF EXISTS SentimentsPipe')
	sqliteConnection.commit()
cursor.execute('CREATE TABLE IF NOT EXISTS SentimentsPipe(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, tweet_id text, class text, positive_sent text, negative_sent text, neutral_sent text)')
sqliteConnection.commit()
for index in range(len(tweets)):
	cursor.execute("INSERT INTO SentimentsPipe (tweet_id, class, positive_sent , negative_sent , neutral_sent) VALUES (?,?,?,?,?)" , (str(tweets[index].tId), str(tweets[index].tSentimentClasses), str(ast.literal_eval(tweets[index].tSentimentProbabilities)[0][1]), str(ast.literal_eval(tweets[index].tSentimentProbabilities)[1][1]), str(ast.literal_eval(tweets[index].tSentimentProbabilities)[2][1])))
	sqliteConnection.commit()
cursor.close()
if sqliteConnection:
	sqliteConnection.close()


