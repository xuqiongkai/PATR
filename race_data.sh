wget http://slanglab.cs.umass.edu/TwitterAAE/TwitterAAE-full-v1.zip

unzip -p TwitterAAE-full-v1.zip TwitterAAE-full-v1/twitteraae_all > twitteraae_all

mkdir race_data
python make_race_data.py twitteraae_all race_data/race_data.obj race_data