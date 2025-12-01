import pandas as pd
#import pickle 
import numpy as np
from sklearn.preprocessing import StandardScaler
#df_2023= pd.read_csv("pitches_2023.csv")
#df_2024=pd.read_csv("pitches_2024.csv")
#df_2025=pd.read_csv("pitches_2024.csv")

'''# No longer need to run this once the dictionaries are loaded
years = [(df_2023, 2023), (df_2024, 2024), (df_2025, 2025)]

lefty_pitchers = {}
righty_pitchers = {}

for frame, year in years:
    # Select relevant columns and drop NaNs
    df = frame[['player_name', 'pitch_type', 'release_speed', 'release_pos_x',
                'release_pos_z', 'p_throws', 'release_extension', 'pfx_x', 'pfx_z']].dropna()

    # Group by pitcher
    pitchers = df.groupby('player_name')

    for pitcher_name, pitcher_data in pitchers:
        # Extract throwing hand (should be the same for the whole group)
        throwing_hand = pitcher_data['p_throws'].iloc[0]

        # Compute mean stats by pitch type
        pitch_groups = pitcher_data.groupby('pitch_type')[[
            'release_speed', 'release_pos_x', 'release_pos_z',
            'release_extension', 'pfx_x', 'pfx_z'
        ]].mean()

        # Build pitch summary
        pitch_summary = {
            pitch_type: row.tolist()
            for pitch_type, row in pitch_groups.iterrows()
        }

        # Assign to correct dictionary
        pitcher_key = (pitcher_name, year)
        pitcher_data_dict = {'pitches': pitch_summary}

        if throwing_hand == 'L':
            lefty_pitchers[pitcher_key] = pitcher_data_dict
        elif throwing_hand == 'R':
            righty_pitchers[pitcher_key] = pitcher_data_dict
        else:
            # Optional: handle ambidextrous or unknown if needed
            pass

#Compute speed difference from fastest pitch

def apply_speed_diff(pitcher_dict):
    for key, data in pitcher_dict.items():
        pitch_speeds = {pitch: features[0] for pitch, features in data['pitches'].items()}
        max_speed = max(pitch_speeds.values())
        for pitch, features in data['pitches'].items():
            speed = features[0]
            speed_diff = 0 if speed == max_speed else max_speed - speed
            data['pitches'][pitch][0] = speed_diff

apply_speed_diff(lefty_pitchers)
apply_speed_diff(righty_pitchers)

# save the dictionaries so I don't have to recompute them every time
with open('lefty_pitchers.pkl', 'wb') as f:
    pickle.dump(lefty_pitchers, f)

with open('righty_pitchers.pkl', 'wb') as f:
    pickle.dump(righty_pitchers, f)


'''


def build_scaler(pitcher_dict):
    all_features = [] # creates a scale for alll the different features
    for data in pitcher_dict.values():
        for vec in data["pitches"].values():
            all_features.append(vec)
    scaler = StandardScaler().fit(np.array(all_features)) # will now get the zscore for each part of each pitch
    return scaler # 

def scale_pitcher_dict(pitcher_dict, scaler):
    '''Using the scaler on the MLB dictionary'''
    scaled = {}
    for key, val in pitcher_dict.items():
        scaled_pitches = {
            pt: scaler.transform([vec])[0]
            for pt, vec in val["pitches"].items()
        }
        scaled[key] = {"pitches": scaled_pitches}
    return scaled


def compute_pitch_distance(vec1, vec2):
        return np.linalg.norm(vec1 - vec2) #find the euclidean distance between the two normalized vectors

def find_most_similar_pitcher(user_pitcher, mlb_pitchers, scaler):
    user_scaled = scale_pitcher_dict({"user": user_pitcher}, scaler)["user"]
    mlb_scaled = scale_pitcher_dict(mlb_pitchers, scaler)

    user_pitch_types = set(user_scaled["pitches"].keys()) # no duplicates
    results = []

    for pitcher_key, data in mlb_scaled.items():
        mlb_pitch_types = set(data["pitches"].keys())
        common = user_pitch_types & mlb_pitch_types

        dists = []
        for pitch in common:
            user_vec = np.array(user_scaled["pitches"][pitch])
            mlb_vec = np.array(data["pitches"][pitch])
            d = compute_pitch_distance(user_vec, mlb_vec)
            dists.append(d)

        if len(dists) == 0:
            continue  # skip if they have no pitch type overlaps

        similarities = [100 - d for d in dists]
        similarity = np.mean(similarities)
        overlap_factor = len(common) / len(user_pitch_types)
        final_score = 0.85 * similarity + 0.15 * (overlap_factor * 100)

        
        results.append((pitcher_key,final_score, len(common)))

    results.sort(key=lambda x: x[1], reverse=True)
    return results
