import pandas as pd
import twint
import networkx as nx
import matplotlib.pyplot as plt
import time

# Depth of recursion
MAX_DEPTH = 3

# Twint requires these apparently:
c = twint.Config()
c.Utc = True
c.Full_text = True
c.Hide_output = True
c.Store_object = True
c.Limit = 250

# Get Elon Musk's tweets
c.Username = "elonmusk"
twint.run.Search(c)
tweets = twint.output.tweets_list

# Create the graph
G = nx.DiGraph()


def add_replies(tweet, depth=0):
    """
    Recursively add replies to the graph.
    """
    if depth > MAX_DEPTH:
        return
    reply_to = tweet.reply_to
    if reply_to:
        if isinstance(reply_to, dict):
            reply_to_id = str(reply_to.get("id", ""))
        elif isinstance(reply_to, list):
            reply_to_dict = reply_to[0]
            reply_to_id = str(reply_to_dict.get("id", ""))
        G.add_edge(str(tweet.user_id), reply_to_id)
        c = twint.Config()
        c.Utc = True
        c.Full_text = True
        c.Username = None
        c.Search = "from:" + tweet.username + " conversation_id:" + reply_to_id
        c.Hide_output = True
        c.Store_object = True
        c.Store_object_tweets_list = True
        twint.run.Search(c)
        time.sleep(10)
        reply_to_tweet = twint.output.tweets_list[-1]
        add_replies(reply_to_tweet, depth=depth+1)


# Add Elon Musk's tweets and their replies
for tweet in tweets:
    add_replies(tweet)

# Write the graph to a CSV file
nx.write_edgelist(G, "twitter_social_network.csv", delimiter=",", data=False)

# Load the edge list into a pandas DataFrame
df = pd.read_csv("twitter_social_network.csv",
                 header=None, names=["source", "target"])

# Write the edge table to a CSV file
df.to_csv("twitter_social_network_table.csv", index=False)
