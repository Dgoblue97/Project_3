## Your name:Daniel Eilender
## The option you've chosen: 2
# Put import statements you expect to need here!
###### INSTRUCTIONS ###### 

# An outline for preparing your final project assignment is in this file.

# Below, throughout this file, you should put comments that explain exactly what you should do for each step of your project. You should specify variable names and processes to use. For example, "Use dictionary accumulation with the list you just created to create a dictionary called tag_counts, where the keys represent tags on flickr photos and the values represent frequency of times those tags occur in the list."

# You can use second person ("You should...") or first person ("I will...") or whatever is comfortable for you, as long as you are clear about what should be done.

# Some parts of the code should already be filled in when you turn this in:
# - At least 1 function which gets and caches data from 1 of your data sources, and an invocation of each of those functions to show that they work 
# - Tests at the end of your file that accord with those instructions (will test that you completed those instructions correctly!)
# - Code that creates a database file and tables as your project plan explains, such that your program can be run over and over again without error and without duplicate rows in your tables.
# - At least enough code to load data into 1 of your dtabase tables (this should accord with your instructions/tests)

######### END INSTRUCTIONS #########

# Put all import statements you need here.

# Begin filling in instructions....
import unittest
import itertools
import collections
import tweepy
import twitter_info # same deal as always...
import json
import sqlite3
import requests_oauthlib
import webbrowser
import requests 
from pprint import pprint

consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Set up library to grab stuff from twitter with your authentication, and return it in a JSON format 
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

movie_1 = 'Gladiator'
movie_2 = 'Frozen'
movie_3 = 'Avatar'
movie_list = [] # making a list of movie titles
movie_list.append(movie_1)
movie_list.append(movie_2)
movie_list.append(movie_3)


CACHE_FNAME = "SI206_final_project_cache.json"
# Put the rest of your caching setup here:
try:
	cache_file = open(CACHE_FNAME,'r')
	cache_contents = cache_file.read()
	cache_file.close()
	CACHE_DICTION = json.loads(cache_contents)
except:
	CACHE_DICTION = {}


def getwithcaching(movie_title): # function to either get movie data from cache or requests movie adata using title
	BASE_URL='http://www.omdbapi.com?'
	if movie_title in CACHE_DICTION:
		# print ('using cache')
		response_text=CACHE_DICTION[movie_title]
	else:
		# print ('fetching')
		response = requests.get(BASE_URL, params={'t':movie_title})
		CACHE_DICTION[movie_title] = response.text
		response_text = response.text
		
		# print (type(response_text))
		cache_file = open(CACHE_FNAME, "w")
		cache_file.write(json.dumps(CACHE_DICTION))
		cache_file.close()
	return (json.loads(response_text))

movie_data_list =[] # Making a list of movie data dictionarys
for movie in movie_list:
	data = getwithcaching(movie)
	movie_data_list.append(data)

# print (movie_data_list[0])
# for movie in movie_data_list:
# 	print (movie_data_list)
# def get_user_tweets(input_word):



class Movie(object): # Movie class that pulls data from movie dictionaries when making an instance
	def __init__(self, movie_data):
		self.title = movie_data['Title']
		self.release_year = movie_data['Year']
		self.plot = movie_data['Plot']
		self.tomatoCriticMeter_string = movie_data["Metascore"]
		self.tomatoCriticMeter = int(self.tomatoCriticMeter_string) 
		self.tomatoUserMeter_string = movie_data['Ratings'][1]['Value'][:1]
		self.tomatoUserMeter = int(self.tomatoUserMeter_string)
		self.rated = movie_data['Rated'].encode('utf-8')  
		self.id = movie_data['imdbID']
		self.director = movie_data['Director']
		self.imdb_rating_string = (movie_data['imdbRating'])
		self.imdb_rating = float(self.imdb_rating_string)
		self.movie_data = movie_data

	def rating(self):
		if self.rated =="NC-17":
			return "The rating for " + self.title + " is " + self.rated + ": No One 17 and Under Admitted. Clearly adult. Children are not admitted."
		elif self.rated =='R':
			return "The rating for " + self.title + "is" + self.rated + ": Under 17 requires accompanying parent or adult guardian. Contains some adult material. Parents are urged to learn more about the film before taking their young children with them."
		elif self.rated =="PG-13":
			return "The rating for " + self.title + "is" + self.rated + ": Some material may be inappropriate for children under 13. Parents are urged to be cautious. Some material may be inappropriate for pre-teenagers."
		elif self.rated =="PG":
			return "The rating for " + self.title + "is" + self.rated + ": Some material may not be suitable for children. Parents urged to give 'parental guidance'. May contain some material parents might not like for their young children."
		elif self.rated =="G":
			return "The rating for " + self.title + "is" + self.rated + ": All ages admitted. Nothing that would offend parents for viewing by children."
		else:
			return self.title + " is unrated, viewers should watch at their own discretion."    

	def getMovieAudience(self):
		if self.tomatoCriticMeter > self.tomatoUserMeter:
			return "The Critics like it more"
		elif self.tomatoCriticMeter < self.tomatoUserMeter: 
			return "The Audience likes it more"
		elif self.tomatoCriticMeter == self.tomatoUserMeter:    
			return "Critics and Audience like it the same"
		else:	
			return "Oops thats not a movie!"	
	def movieAppeal(self):
		if self.tomatoCriticMeter + self.tomatoUserMeter > 180:
			return "This movie is very highly acclaimed"
		elif self.tomatoCriticMeter + self.tomatoUserMeter > 140:
			return "This movie was fairly well recieved"	
		elif self.tomatoCriticMeter + self.tomatoUserMeter > 100:
			return "This movie had mixed reviews"
		elif self.tomatoCriticMeter + self.tomatoUserMeter < 100:
			return "This movie was not recieved well"
		else:
			return "Oops, thats not a movie!"					

	def __str__(self):
		return 'The movie {} came out in {}. The plot is: {}'.format(self.title, self.release_year, self.plot)
      
	def num_of_languages(self):
		all_languages = self.movie_data['Language'].split(',')
		return len(all_languages)
	def get_actors(self):
		list_of_actors = self.movie_data['Actors'].split(',')
		return str(list_of_actors)	
list_of_movie_instances = []

for movie in movie_data_list: # Using a for loop to run each movie dictionary into the class Movie and make an instance. Then appending these instances into a list
	movie_instance = Movie(movie)
	list_of_movie_instances.append(movie_instance)


movie_tuple_list = []

for movie_instance in list_of_movie_instances: # This block of code is creating a list of three movie tuples containing data on three different movies
	new_tuple = (movie_instance.id, movie_instance.title, movie_instance.plot, movie_instance.rated, movie_instance.director, movie_instance.imdb_rating, movie_instance.num_of_languages(), movie_instance.get_actors(), movie_instance.getMovieAudience())
	movie_tuple_list.append(new_tuple)
		



#************TWITTER**************************************************************


twitter_cache_file = 'twitter_cache_file.json'
try:
	file = open(twitter_cache_file, 'r')
	file_contents = file.read()
	twitter_cache_dictionary = json.loads(file_contents)
except:
	twitter_cache_dictionary = {}


def get_tweetdata_with_caching(input_word):

	unique_identifier = input_word
	if unique_identifier in twitter_cache_dictionary: # if it is...
		twitter_results = twitter_cache_dictionary[unique_identifier]
		# print('using twitter cache') # grab the data from the cache!
		return twitter_results['statuses']
	else:
		twitter_results = api.search(q = unique_identifier,)
		# print ('fetching twitter data')
		twitter_cache_dictionary[unique_identifier] = twitter_results
		f=open(twitter_cache_file, "w")
		f.write(json.dumps(twitter_cache_dictionary))
		f.close()
		
		return twitter_results['statuses']


List_twitter_search_titles = [] # Getting the titles of three movies from the list of movie instances
for instance in list_of_movie_instances:
	title = instance.title
	List_twitter_search_titles.append(title)



List_of_twitter_data_list = [] # Getting twitter data from either a cache or API by searching by movie title
for search_term in List_twitter_search_titles:
	
	data = get_tweetdata_with_caching(search_term)
	List_of_twitter_data_list.append(data)
	

class Tweet(object): # a class to pull out data from a list of twitter data, input is a list
		def __init__(self, tweet_data):
			for tweets in tweet_data:
				self.tweet_id = tweets['id_str']
				self.text = tweets['text']
				self.user_id = tweets['user']['id_str']
				self.favorites = tweets['favorite_count']
				self.retweets = tweets['retweet_count']
				


List_of_tweet_instances = []

for data in List_of_twitter_data_list:
	instance = Tweet(data)
	List_of_tweet_instances.append(instance)
List_of_tweet_tuples = []
for instance in List_of_tweet_instances:
	new_tuple = (instance.tweet_id, instance.text, instance.user_id, instance.favorites, instance.retweets)	
	List_of_tweet_tuples.append(new_tuple)
		
	
# Put data into a list of tuples

# Then insert this data into Tweets Table



#***********USERS*****************************************************************

twitter_user_file = 'twitter_user_cache.json'

try:
	twitter_data_cache = open(twitter_user_file,'r')
	twitter_user_cachecontents = twitter_data_cache.read()
	twitter_user_dict = json.loads(twitter_user_cachecontents)

except:

	twitter_user_dict = {}



class TweetUser(object): # a class to pull out data from a list of twitter data, input is a list
		def __init__(self, tweet_data):
			for tweets in tweet_data:
				self.tweet_id = tweets['id_str']
				self.text = tweets['text']
				self.user_id = tweets['user']['id_str']
				self.favorite_count = tweets['user']['favourites_count']
				self.num_of_followers = tweets['user']['followers_count']
				self.tweet_count = tweets['user']['statuses_count']
				self.screen_name = tweets['user']['screen_name']



List_of_tweet_User_instances = []

for data in List_of_twitter_data_list:
	instance = TweetUser(data)
	List_of_tweet_User_instances.append(instance)

List_of_tweet_user_tuples = []	
for instance in List_of_tweet_User_instances:
	new_tuple = (instance.user_id, instance.screen_name, instance.favorite_count, instance.num_of_followers, instance.tweet_count)	
	List_of_tweet_user_tuples.append(new_tuple)
	# if instance.screen_name not in twitter_user_dict:
	# 	screename = instance.screen_name
	# 	twitter_user_dict[screename] = 
	# 	twitter_data_cache = open(twitter_user_file,'w')
	# 	twitter_user_file.write()
	# 	twitter_user_dict = json.loads(twitter_user_cachecontents)

	# Caching Username here^^^^^^

	
# Follow similar pattern as above to make instances than cache by screename				


# Once data is acquired put it into a list of tuples

# Then insert this data into the Users Table







#*****************SQL**************************************************************





conn = sqlite3.connect('Final_Project.db')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Tweets')
cur.execute('DROP TABLE IF EXISTS Users')
cur.execute('DROP TABLE IF EXISTS Movies')




table_spec = 'CREATE TABLE IF NOT EXISTS Tweets(tweet_id TEXT PRIMARY KEY, text TEXT, user_id TEXT, title TEXT, favorites INTEGER, retweets INTEGER)'
cur.execute(table_spec)

table_spec = 'CREATE TABLE IF NOT EXISTS Users(user_id TEXT PRIMARY KEY, screen_name TEXT, num_favs INTEGER)'
cur.execute(table_spec)

table_spec = 'CREATE TABLE IF NOT EXISTS Movies(Movie_id TEXT PRIMARY KEY, Title TEXT, Plot TEXT, Rated TEXT, Director TEXT, imbd_rating INTEGER, num_of_languages INTEGER, Actors TEXT, Audience TEXT)'
cur.execute(table_spec)
conn.commit()

statement = 'INSERT OR IGNORE INTO Movies Values (?,?,?,?,?,?,?,?,?)'
for movie in movie_tuple_list:
	cur.execute(statement, movie)
conn.commit()	


conn.close()





# Join statments


# Statment 1 will be an INNER Join matching movie title in MOVIES and favorites and user_id TWeets to see which tweet that mentioned a movie was favorited the most and the user_id of that person

# Statement 2 will Join getMovieAudience, Plot, Actors, and Imdb_rating to return important information about the Movie

# Statement 3 will be an InnerJoin selecting Tweets favorites with Movies titles and year to see  if tweets about more recent movies get more favorites

#*************************DATA PROCESSING**************************************



# mapping

# collections

#list comprehension

#dictionary accumulation










#******** Write to a Text File*******************************



# Write my output from the 4 data manipulations into  test file


# Put your tests here, with any edits you now need from when you turned them in with your project plan.

# Attempt is an "instance of a movie"

class Tests(unittest.TestCase):
	# Write more test cases
	def test_1(self):
		attempt = list_of_movie_instances[0]
		self.assertEqual(type(attempt.movieAppeal()), type('a'), "testing type of return value of movieAppeal method in the Movie Class")
	def test_2(self):
		attempt = list_of_movie_instances[0]
		self.assertEqual(attempt.num_of_languages(), 1, 'Testing the return value of num_of_langauges method')	
	def test_3(self):
		attempt = list_of_movie_instances[0]
		self.assertEqual(attempt.title, movie_1, 'testting side effect of the consturctor to see if the instance variable is correct')
	def test_4(self):
		attempt = list_of_movie_instances[0]
		self.assertEqual(attempt.imdb_rating, 8.5, 'Testing the side effect of the constructor to see if if the instance variable self.imdb_rating returns the correct rating')
	def test_5(self):
		attempt = list_of_movie_instances[0]
		self.assertEqual(attempt.getMovieAudience(), 'The Critics like it more', 'Testing the return value of the getMovideAudience method')
	# def test_6(self):
	# 	conn = sqlite3.connect('Final_project.db')
	# 	cur = conn.cursor()
	# 	cur.execute('SELECT * FROM Users');
	# 	result = cur.fetchall()
	# 	self.assertTrue(len(result[1])==3,"Testing that there are 3 columns in the Users database")
	# 	conn.close()
	def test_7(self):
		self.assertEqual(len(list_of_movie_instances), 3, 'Testing that the list of Movie instances has 3 or more instances of a movie') 
	def test_8(self):
		conn = sqlite3.connect('Final_project.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Movies');
		result = cur.fetchall()
		self.assertTrue(len(result[2])==9,"Testing that there are 9 columns in the Movies table")
		conn.close()	

## Remember to invoke all your tests...

unittest.main(verbosity=2) 