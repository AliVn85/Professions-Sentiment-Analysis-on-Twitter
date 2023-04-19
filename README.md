# Professions Sentiment Analysis on Twitter
 ## Master research lab on "Monitoring of education and training on Twitter"
 
This is a bundle of scraper for Twitter and a SpaCy equipped pipeline for analyzing sentiments regarding a set of input values primarily focused on German professions.

###  Note 
This is a research lab study as part of the master of Web and Data Science course at UniKoblenz.
## Names of students
- Ali Vahdatnia
- Danoosh Peachkah
## Underlying paper
*[Add the link of the paper (To be allowed by supervisor)]*

# How to install/Quick Start

First, clone the repository locally, then do the preparations below:
1. Acquire a Twitter authentication token for Tweepy and assign the tokens to the scraper.py script.
2. For the scraper to work, you will need a CSV file that has a series of keywords separated by semicolon. The scraper will group each keywords per line from the 1st one - not the 0th. 

Second, you may run the Scraper/scrp.py using the following command in the folder where the said script exists:
```
python3 scrp.py -f yourFile.csv
```
After some time, a database will appear with all the scrapped Tweets.

Next, using the following commands the result of sentiment analysis for each Tweet will be ready in the database - in the Pipeline folder:
```
python3 reader.py -d "../database.db" |  python3 spaCy.py | python3 writer.py -d "../database.db"
```
Lastly, using the examples provided in the Report folder, you may experiment with the visualizations and further monitoring.

## Create files and folders

The file explorer is accessible using the button in left corner of the navigation bar. You can create a new file by clicking the **New file** button in the file explorer. You can also create folders by clicking the **New folder** button.


## Implementation
### Hardware requirements:
-   1.6 GHz or faster processor
-   1 GB of RAM
### Software requirements:
-   OS X El Capitan (10.11+)
-   Windows 8.0, 8.1, and 10, 11 (32-bit and 64-bit)
-   Linux (Debian): Ubuntu Desktop 16.04, Debian 9
-   Linux (Red Hat): Red Hat Enterprise Linux 7, CentOS 7, Fedora 34
-	Jupyter Notebook
-	Python Version: Python 3.10.6       
	- de_core_news_sm==3.5.0
	- dkpro_cassis==0.7.3
	- emoji==0.6.0
	- geojson==3.0.1
	- geopandas==0.12.2
	- germansentiment==1.1.0
	- ipyleaflet==0.17.2
	- ipywidgets==8.0.4
	- matplotlib==3.7.0
	- nltk==3.8.1
	- pandas==1.5.3
	- requests==2.25.1
	- spacy==3.5.0
	- spacymoji==3.0.1
	- sqlite3==3.37.2
	- turfpy==0.0.7
	- tweepy==4.12.1
	- de_core_news_sm==3.5.0

-	Active Internet Connection

## References
<a id="1">[1]</a> 
The following file is used in this repository from the GitHub repo [from pensnarik](https://github.com/pensnarik/german-cities): germany.json


