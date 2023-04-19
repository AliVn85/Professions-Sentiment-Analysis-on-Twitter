import spacy
import de_core_news_sm
from spacymoji import Emoji
import sqlite3
from sqlite3 import Error
from germansentiment import SentimentModel
import ast
import sys
from cassis import *

# Preparing the Cassis and its structure TypeSystem
with open('typesystem.xml', 'rb') as f:
    typesystem = load_typesystem(f)

lines = ""
for line in sys.stdin:
    lines=lines+line

cas = load_cas_from_xmi(lines,typesystem=typesystem)
tweets = cas.select('Tweet')

# Loading SpaCy library
nlp = spacy.load("de_core_news_sm")
nlp.add_pipe("emoji", first=True)

# Loading Sentiment analyzer library
model = SentimentModel()

# Generating a list of tokenized Tweet texts (Named Entity Recognition)
for index in range(len(tweets)):
	lst = []
	strg = ''
	for token in nlp(tweets[index].tText):
		if token.is_alpha == True:
			strg = strg + str(token) + " "
	lst.append(strg)
	# Analyzing sentiments of each tokenized Tweet
	classes, probabilities = model.predict_sentiment(lst, output_probabilities = True) 
		
	tweets[index].tSentimentClasses = str(classes[0])
	tweets[index].tSentimentProbabilities = str(probabilities[0])
	
outputed = cas.to_xmi()
print(outputed)


