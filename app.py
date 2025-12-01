import streamlit as st
import pickle 
from similarity import find_most_similar_pitcher,build_scaler
#Load pitcher dictionary
@st.cache_resource
def load_pitcher_data():
    with open('lefty_pitchers.pkl', 'rb') as f:
        lefties = pickle.load(f)
    with open('righty_pitchers.pkl', 'rb') as f:
        righties = pickle.load(f)
    return lefties, righties

lefty_pitchers, righty_pitchers = load_pitcher_data()
scaler_left = build_scaler(lefty_pitchers)
scaler_right=build_scaler(righty_pitchers)

st.title("MLB Pitcher Similarity Finder")

# Handedness selection
handedness = st.radio("Select your throwing hand:", ["Right", "Left"])
if handedness == "Right":
    target_dict = righty_pitchers
    scaler = scaler_right
else:
    target_dict = lefty_pitchers
    scaler = scaler_left
#Idea for trackman data to be uploaded as a csv
#uploaded_file= st.file_uploader("Your Trackman Data") 
st.subheader("Enter your pitch metrics:")
st.caption("First, enter your general release info (applies to all pitches).")

# One-time release metrics
col1, col2, col3 = st.columns(3)
with col1:
    release_pos_x = st.number_input("Release Side(ft)", value=0.0, step=0.1)*-1 #mlb release side is flipped from rapsodo
with col2:
    release_height = st.number_input("Release height(ft)", value=6.0, step=0.1)
with col3:
    release_ext = st.number_input("Extension(ft)", value=6.0, step=0.1)

st.divider()

st.subheader("Enter your pitch types:")
st.caption("Each pitch should have: speed(mph), horizontal movement (inches), induced vertical break (inches)")

# Dynamic pitch input (simplified)
user_pitches = {}
pitch_types = st.multiselect("Which pitch types do you throw?", ["FF", "SL", "CH", "CU", "SI", "FC", "SP"])
for pitch in pitch_types:
    col1, col2, col3 = st.columns(3)
    with col1:
        pitch_speed = st.number_input(f"{pitch} mph", value=0.0)
    with col2:
        pfx_x = st.number_input(f"{pitch} horizontal movement (inches)", value=0.0) / -12 # to adjust for inches and MLB is flipped movement from rapsodo
    with col3:
        pfx_z = st.number_input(f"{pitch} ivb (inches)", value=0.0) / 12

    user_pitches[pitch] = [
        pitch_speed,
        release_pos_x,
        release_height,
        release_ext,
        pfx_x,
        pfx_z,
    ]
speeds=[]
for i in user_pitches.values():
    speeds.append(i[0])
if speeds:
    max_speed=max(speeds)
    for i in user_pitches.values():
        i[0]-=max_speed # get the speed differential

    
if st.button("Find Similar Pitchers"):
    if len(user_pitches) == 0:
        st.warning("Please enter at least one pitch type.")
    else:
        user_pitcher = {"pitches": user_pitches}
        results = find_most_similar_pitcher(user_pitcher, target_dict, scaler)

        if not results:
            st.error("No pitchers found with enough overlapping pitch types.")
        else:
            st.success("Here are your top matches:")
            for (name, year), score, overlap in results[:5]:
                st.write(f"**{name} ({year})** — Similarity: {score:.2f} | Pitch Overlap: {overlap}")
