#!/usr/bin/env python
# coding: utf-8

# import some libraries to process tweets and extract sentiments
import time
from datetime import datetime
import json
from textblob import TextBlob

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

# import the twitter file which contains your twitter access credentials.
# This consist of four identifiers: 
# 1. Consumer Key (API Key)
# 2. Consumer Secret (API Secret)
# 3. Access Token
# 4. Access Token Secret
import twitter_credential
 

class TwitterStreamer():
    """
    Class for streaming live tweets.
    """
    def __init__(self):
        # no need for a constructor, do nothing
        pass
    
    def stream_tweets(self, file_name, long_lat_pos):
        """this handles Twitter authetication and the connection to Twitter Streaming API
        
        parameters
        ----------
        file_name: string
            the name of the file where the sentiments extracted will be stored
            it will be passed to the stream listener
        long_lat_pos: list
            a list of longitude and latitude values, acting as a bounding box which indicate
            an area. go to https://boundingbox.klokantech.com/ to get a bounding box for 
            desired area
        """
        listener = StdOutListener(file_name)
        auth = OAuthHandler(twitter_credential.CONSUMER_KEY, twitter_credential.CONSUMER_SECRET)
        auth.set_access_token(twitter_credential.ACCESS_TOKEN, twitter_credential.ACCESS_TOKEN_SECRET)
        stream = Stream(auth, listener)
        # filter Twitter Streams to capture data by the location and run in a new thread. Streams
        # do not terminate unless the connection is closed blocking the thread. Tweepy offers 
        # a convenient is_async parameter on filter so the stream will run on a new thread.
        stream.filter(locations=long_lat_pos, is_async=True)
        

class StdOutListener(StreamListener):
    """
    To listen to the Twitter stream we will need to make an instance of the Tweepy StreamListener.
    We will override the following functions:
    
    1. **__init__** to set up the initialisation parameters for our particular listener
    2. **on_data** to listen to Tweets
    3. **on_error** to catch any problems (especially Twitter telling us off...)
    """
    def __init__(self, file_name, time_limit=3600):
        """construct for the listener
        
        parameters
        ----------
        file_name: string
            the name of the file where the sentiments extracted will be stored
        time_limit: int
            this is the number of seconds you want the stream to run
        """
        self.file_name = file_name
        self.time_limit = time_limit
        self.start_time = time.time()

    def on_data(self, data):
        # lets collect the stream for a specified time if no time is specified
        # then the default time will be one hour. for as long as we haven't
        # hit the time limit, continue streaming
        if int(time.time()-self.start_time) <= self.time_limit:
            # make sure that exception encountered are handled
            try:
                # tweets come in json format. use the json library to 
                # extract tweet to allow for easy handling
                decoded = json.loads(data)
                tweet = decoded['text'].encode('ascii', 'ignore')
                # lets grab the sentiment using text blob and retrieve 
                # sentiments which are less than 70% subjective
                analysis = TextBlob(tweet)
                sentiment_value, subjectivity = analysis.sentiment
                # convert the values to string for file writing
                sentiment_value = str(sentiment_value)
                timestamped_sentiment_value = str(datetime.fromtimestamp(time.time()))
                timestamped_sentiment_value = sentiment_value+','+timestamped_sentiment_value
                if subjectivity*100 <= 70:
                    output_file = open(self.file_name, "a")
                    # example written value: '0.5,2019-05-12 18:28:46.673000'
                    output_file.write(timestamped_sentiment_value)
                    output_file.write('\n')
                    output_file.close()
                return True
            except BaseException as e:
                print("Error on_data: %s" % str(e))
            return True
        else:
            # time is up, so stop streaming
            return False
          
    def on_error(self, status):
        # if twitter tells us off return false
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False
        else:
            return True
