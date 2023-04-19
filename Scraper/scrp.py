import pandas as pd
import tweepy
import csv
import time
import datetime
import sqlite3
import os
import math
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--index", dest="key_index",default="0", action="store", type="string",
                  help="Index of keyword to be scraped", metavar="filename")
parser.add_option("-f", "--file", dest="input_file",default="5Snd.csv", action="store", type="string",
                  help="Index of keyword to be scraped", metavar="filename")
args = parser.parse_args()
(options, args) = parser.parse_args()

startScanIndex = int(options.key_index) #to be defined in case of continuing 
start = datetime.datetime(2006,3,31)

client = tweepy.Client(
	bearer_token = "",
	consumer_key="",
	consumer_secret="",
	access_token="",
	access_token_secret="",
	return_type = dict, wait_on_rate_limit=True
)

# Reading the file and extracting the keywords
with open(options.input_file) as file:
	tmp = file.readlines()

lst = []
for item in tmp:
	lst.append((item.replace("\n", "")).split(";"))

# Used for indicating the processing time
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
print("\n Start: ",current_time)

# Calculationg and receiving the results based on the keywords 
if (startScanIndex==0): #in case you want to continue, we do not want to destroy the old scanned data
	try:
		print("Deleting the old database...")
		os.remove('../database.db') # Refreshing the database to avoid the table conflict 
	except:
		print("...Old database not found, Creating a new database")

conn = sqlite3.connect('../database.db')
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS Tweets(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, job_id text, job_title text, place_id number, tweet_id number,tweet_txt text, lang text, public_metrics_retCount number, public_metrics_repCount number, public_metrics_likeCount number, public_metrics_qouCount number, public_metrics_ImpCount number, createdAt DATETIME, scrapedTime DATETIME, authorId number)')
conn.commit()

c.execute('CREATE TABLE IF NOT EXISTS Hashtags(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, tweet_id number, hashtags text)')
conn.commit()

c.execute('CREATE TABLE IF NOT EXISTS Locations(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, place_id number, tweet_id text, location_name text, location_type text, location_country text, location_code text, location_bbox text)')
conn.commit()

counter = 0 
memoryLst=[]

successfullyAddedIndex = 0;

for jobDetail in lst[:-1]:
	for search_item in jobDetail[1:]:
		counter = counter + 1
		
		text_file = open("checkpoint.txt", "w")
		text_file.write("Last successfully processed index: "+str(counter-1)+".\nPlease use '-i' and the number showed here to continue processing.")
		text_file.close()
		
		print(f"Last Proccessed Item is        {counter}.")
		if (startScanIndex <= counter):
			try:
				print("Start doing work for index    ", counter," : ", search_item)
				tweets = client.search_all_tweets(	query=search_item, max_results=500, start_time = start,
									tweet_fields = ['id', 'author_id','created_at','text','source','lang','geo','public_metrics'],
								    	user_fields = ['id', 'name','username','location','verified'],
								    	expansions = ['geo.place_id', 'author_id'],
									place_fields = ['id','name', 'full_name', 'country', 'country_code', 'geo', 'place_type'])
				
				time.sleep(1) #Needed for solving the issues caused by rate limitations
				df = pd.json_normalize(tweets) # Flattens the JSON data object childs
				df["job_title"] = search_item
				df["job_id"] = jobDetail[0]
				df["scraped_time"] = str(datetime.datetime.now())
				for i in range(len(df)):
					if ("data" not in df):
						print("Finished doing work for index ", counter," : ", search_item)
						continue
					else:		
						tweetsData = df["data"].iloc[i]
						for j in range(len(tweetsData)):
							
							searchedTerm = df["job_title"].iloc[i]
							searchedTermId = df["job_id"].iloc[i]
							
							tPlaceName = ""
							tPlaceType = ""
							tPlaceCountry = ""
							tPlaceCountryCode = ""
							tPlaceGeoBbox = ""
							tPlaceId = ""
							tHashtags = ""

							tAuthId = tweetsData[j]["author_id"]
							tId = tweetsData[j]["id"]
							tText = tweetsData[j]["text"]
							tLAng = tweetsData[j]["lang"]
							tPuRet = tweetsData[j]["public_metrics"]["retweet_count"]
							tPuRep = tweetsData[j]["public_metrics"]["reply_count"]
							tPuLik = tweetsData[j]["public_metrics"]["like_count"]
							tPuQou = tweetsData[j]["public_metrics"]["quote_count"]
							tPuImp = tweetsData[j]["public_metrics"]["impression_count"] 
							tCreDate = tweetsData[j]["created_at"]
							tScrTime = df["scraped_time"].iloc[i]
										
							if '#' in tweetsData[j]["text"]:
								lst = []
								for wrd in tweetsData[j]["text"].split(sep=None, maxsplit=-1):								
									if wrd[0] == '#':
										lst.append(wrd)
								tHashtags = " ".join(lst)
								c.execute("INSERT INTO Hashtags (tweet_id, hashtags) VALUES (?, ?)", (tId, tHashtags))
								conn.commit()
							if ("includes.places" in df): # Check in case there are no Tweets (NAN) for that Tweet query
								tweetsInclude = df["includes.places"].iloc[i]
								if 'geo' in tweetsData[j]:
									tweet_place_id = tweetsData[j]['geo']['place_id']
									for item in tweetsInclude:
										if(not isinstance(tweetsInclude, float)):
											if item['id'] == tweet_place_id:
												tPlaceName = item["name"]
												tPlaceType = item["place_type"]
												tPlaceCountry = item["country"]
												tPlaceCountryCode = item["country_code"]
												tPlaceGeoBbox = item.get("geo")["bbox"]
												tPlaceId = item["id"]
												c.execute("INSERT INTO Locations (place_id, tweet_id, location_name, location_type, location_country, location_code, location_bbox) VALUES (?, ?, ?, ?, ?, ?, ?)", (tPlaceId, tId, tPlaceName, tPlaceType, tPlaceCountry,tPlaceCountryCode, str(tPlaceGeoBbox)))
												conn.commit()
								
							c.execute("INSERT INTO Tweets (job_id, job_title, place_id, tweet_id, tweet_txt, lang, public_metrics_retCount, public_metrics_repCount, public_metrics_likeCount, public_metrics_qouCount, public_metrics_ImpCount, createdAt, scrapedTime, authorId) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (searchedTermId, searchedTerm, tPlaceId, tId, tText, tLAng, tPuRet, tPuRep, tPuLik, tPuQou, tPuImp, tCreDate, tScrTime, tAuthId))
							conn.commit()
					print("Finished doing work for index ", counter," : ", search_item)
			except Exception as e:
				print("FAILED for index ", counter," : ", search_item, e) # In case of error encountered
				errorCounter = 0
				if (len(memoryLst) > 0):
					for error in memoryLst:
						if (error == search_item):
							errorCounter = errorCounter + 1
						if (errorCounter<=2):
							memoryLst.append(search_item)
							lst.append(search_item)
				else:
					memoryLst.append(search_item)
					lst.append(search_item)
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
print("\n Finish: ",current_time)		

