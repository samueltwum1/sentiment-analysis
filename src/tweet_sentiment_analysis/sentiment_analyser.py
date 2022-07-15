import json
import time
from datetime import datetime

from textblob import TextBlob

from tweepy import Stream
from twitter_credential import (
    ACCESS_TOKEN,
    ACCESS_TOKEN_SECRET,
    CONSUMER_KEY,
    CONSUMER_SECRET,
)


class TwitterStreamer:

    def __init__(self, file_name, long_lat_pos):
        """
        Initialise a Streamer

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
        self.file_name = file_name
        self.long_lat_pos = long_lat_pos

    def stream_tweets(self):
        """
        This handles Twitter authetication and the connection to Twitter Streaming API
        """
        listener = StdOutListener(
            self.file_name,
            CONSUMER_KEY,
            CONSUMER_SECRET,
            ACCESS_TOKEN,
            ACCESS_TOKEN_SECRET,
        )

        # Filter Twitter Streams to capture data by the location and run in
        # a new Streams do not terminate unless the connection is closed.
        listener.filter(locations=self.long_lat_pos, threaded=True)


class StdOutListener(Stream):

    def __init__(self, file_name, *args, time_limit=3600, **kwargs):
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

        super().__init__(*args, **kwargs)

    def on_connection_error(self):
        self.disconnect()

    def on_data(self, data):
        # lets collect the stream for a specified time if no time is specified
        # then the default time will be one hour. for as long as we haven't
        # hit the time limit, continue streaming
        if int(time.time() - self.start_time) <= self.time_limit:
            # make sure that exception encountered are handled
            try:
                # tweets come in json format. use the json library to
                # extract tweet to allow for easy handling
                incoming_tweet = json.loads(data)
                # print(decoded)
                # return True
                tweet = (
                    incoming_tweet["text"].encode("utf-8", "ignore")
                ).decode("utf-8")
                # lets grab the sentiment using text blob and retrieve
                # sentiments which are less than 70% subjective
                analysis = TextBlob(tweet)
                sentiment_value, subjectivity = analysis.sentiment
                # convert the values to string for file writing
                sentiment_value = str(sentiment_value)
                timestamped_sentiment_value = str(
                    datetime.fromtimestamp(time.time())
                )
                timestamped_sentiment_value = (
                    sentiment_value + "," + timestamped_sentiment_value
                )
                if subjectivity * 100 <= 70:
                    output_file = open(self.file_name, "a")
                    # example written value: '0.5,2019-05-12 18:28:46.673000'
                    output_file.write(timestamped_sentiment_value)
                    output_file.write("\n")
                    output_file.close()
                return True
            except Exception as e:
                print("Error on_data: %s" % str(e))
            return True
        else:
            # time is up, so stop streaming
            self.disconnect()
            return False

    def on_request_error(self, status_code):
        # if twitter tells us off return false
        if status_code == 429:
            # returning False in on_data disconnects the stream
            self.disconnect()
        else:
            return True
