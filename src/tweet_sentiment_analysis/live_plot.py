"""
This script uses Twitter data to calculate the happiness in CPT as a 
function of time.  It is a mini project and is accompanied by the
documentation titled "How Happy is Your City?"

This example uses the Tweepy library (www.tweepy.org) to stream  Twitter 
data. It also uses a number of other standard Python libraries, all of 
which are available using pip.
"""

import matplotlib.animation as animation
import matplotlib.dates as md
import matplotlib.pyplot as plt
import numpy as np

from datetime import datetime, timedelta
from matplotlib import style

from sentiment_analyser import TwitterStreamer

# this is just a style sheet to make plots look nicer
style.use("seaborn")
# create a figure and place an axis on it
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)


def animate(i):
    sentiment_values = open("tweet_sentiments.txt", "r").read()
    lines = sentiment_values.split("\n")  # split on new line
    # dictonary for holding plotting values
    plot_vals = dict(sentiment=[], time=[])

    # get only the last twenty values we receive
    for val in lines:
        # it's likely we'll encounter an exception in the float
        # conversion handle that and any exception accordingly
        try:
            # split val. it looks like
            # (0.5,2019-05-12 18:28:46.673000) on comma
            sentiment, timestamp = val.split(",")
            timestamp = timestamp.split(".")[0]
            timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            plot_vals["sentiment"].append(float(sentiment))
            plot_vals["time"].append(timestamp)
        except ValueError:
            # do nothing
            pass

    # ensure we have at least one sentiment from a tweet to plot
    if len(plot_vals["sentiment"]) == 0:
        print("still no tweet yet, waiting for first tweet")
    else:
        ax.clear()
        # set the plotting parameters e.g. labels, plot title,...

        # set limit for y-axis
        ax.set_ylim([-1.1, 1.1])
        y_vals = np.arange(-1, 1.1, 0.2)
        for idx, val in enumerate(y_vals):
            y_vals[idx] = float("%.1f" % val)
        y_vals = list(y_vals)
        ax.set_yticks(y_vals)
        y_vals[0] = "unhappy"
        y_vals[y_vals.index(0)] = "neutral"
        y_vals[-1] = "happy"
        ax.set_yticklabels(y_vals)
        # set limit for x-axis
        # tell matplotlib to treat x-axis values as date objects
        ax.xaxis_date()
        xfmt = md.DateFormatter("%H:%M:%S")
        ax.xaxis.set_major_formatter(xfmt)
        ax.set_xlim(
            [
                plot_vals["time"][-1] - timedelta(seconds=20),
                plot_vals["time"][-1],
            ]
        )
        # set the label and then plot
        ax.set_xlabel("Time (in minutes)")
        ax.set_ylabel("Sentiment")
        ax.set_title(
            "Sentimental Analysis of Tweets from South Africa",
            fontdict={"fontsize": 20, "fontweight": "medium"},
        )
        ax.plot(plot_vals["time"], plot_vals["sentiment"], "--ro")


if __name__ == "__main__":

    location = [16.53, -34.38, 32.53, -22.59]  # this is South Africa

    twitter_streamer = TwitterStreamer("tweet_sentiments.txt", location)
    twitter_streamer.stream_tweets()

    # create a function which will animate our plot
    ani = animation.FuncAnimation(fig, animate, interval=2000)
    plt.show()
