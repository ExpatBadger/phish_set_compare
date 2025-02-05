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

# group by showID
show_songs = df.groupby("showid")["songid"].apply(set).to_dict()

## perform intersections, count shows in common, save the count of shows

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
# writing the full dataframe to csv may produce a very large file:
# similarity_df.to_csv("show_similarities.csv", index=False)
similarity_df_top = similarity_df.head(1000)
similarity_df_top.to_csv("show_similarities_top.csv", index=False)

# Compute the average number of common songs per show
average_common_songs = {
    show: data["total_common"] / data["count"]
    for show, data in show_intersections.items()
}

# Convert to DataFrame
average_common_df = pd.DataFrame(average_common_songs.items(), columns=["showid", "AvgCommonSongs"])
average_common_df = average_common_df.sort_values(by="AvgCommonSongs", ascending=False)

# Save list of most common
average_common_df_top = average_common_df.head(100)
average_common_df_top.to_csv("average_common_songs_top.csv", index=False)

# Save list of least common
average_common_df = average_common_df.sort_values(by="AvgCommonSongs", ascending=True)
average_common_df_bottom = average_common_df.head(100)
average_common_df_bottom.to_csv("average_common_songs_bottom.csv", index=False)

# Save the full list of average common songs
average_common_df.to_csv("average_common_songs.csv", index=False)

# Display results
print("Top show pairs with most songs in common:")
print(similarity_df_top.head(10))

print("Average number of common songs per most common show:")
print(average_common_df_top.head(10))

print("Average number of common songs per least common show:")
print(average_common_df_bottom.head(10))

