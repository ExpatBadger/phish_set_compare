## import needed modules
import pandas as pd
import os
import json
from itertools import combinations

## Set directory of configuration and read in.
project_dir = "C:\\Users\\USERNAME\\Documents\\Projects\\phish_setlists"
os.chdir(project_dir) 

## read in config
with open('config.json', 'r') as openfile:
    # Reading from json file
    config = json.load(openfile)


## pull in prepared data
os.chdir(config["dirs"]["rootdir"]+config["dirs"]["dataprep"]["root_dp"]+config["dirs"]["dataprep"]["interim"])

## create dataframe 
# this is the setlist.csv from the Phish.net API which has showid in column a.
df = pd.read_csv("setlist.csv", index_col=0)

## group by showID

show_songs = df.groupby("showid")["songid"].apply(set).to_dict()

# ## perform intersections, count elements, save the count of elements in the intersection for sorting later

similarities = []
show_intersections = {}

for show1, show2 in combinations(show_songs.keys(), 2):
    common_songs = show_songs[show1] & show_songs[show2]  # Set intersection
    common_count = len(common_songs)
    similarities.append((show1, show2, common_count))
    
    # Track total common songs and number of comparisons per show
    for show in (show1, show2):
        if show not in show_intersections:
            show_intersections[show] = {"total_common": 0, "count": 0}
        show_intersections[show]["total_common"] += common_count
        show_intersections[show]["count"] += 1

# Convert results to a DataFrame
similarity_df = pd.DataFrame(similarities, columns=["show1", "show2", "CommonSongCount"])
similarity_df = similarity_df.sort_values(by="CommonSongCount", ascending=False)

# Compute the average number of common songs per show
average_common_songs = {
    show: data["total_common"] / data["count"]
    for show, data in show_intersections.items()
}


# Identify the most similar shows for each showid, considering multiple ties
# this will allow you to preserve all matching shows that have the same highest common-count value
max_common_songs = similarity_df.groupby("show1")["CommonSongCount"].transform("max")
most_similar_shows = similarity_df[similarity_df["CommonSongCount"] == max_common_songs]
most_similar_shows.to_csv("most_similar_shows.csv", index=False)


print("\nMost similar shows for each show:")
print(most_similar_shows.head(20))
