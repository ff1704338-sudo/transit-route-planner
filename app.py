import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Transit Insight - Route Map", layout="wide")

@st.cache_data
def load_data():
    # Update the filename here to the smaller version
    df = pd.read_csv('route_planner_map_data_small.csv')
    return df

df = load_data()

st.title("🗺️ Interactive Route & Sentiment Map")

# Sidebar for Search
st.sidebar.header("Plan Your Journey")
origin = st.sidebar.selectbox("Origin Station", options=[""] + sorted(df['Stop_name'].unique().tolist()))
destination = st.sidebar.selectbox("Destination Station", options=[""] + sorted(df['Stop_name'].unique().tolist()))

if origin and destination:
    if origin == destination:
        st.warning("Please choose different stations.")
    else:
        # Find shared routes
        orig_routes = set(df[df['Stop_name'] == origin]['Route_long_name'])
        dest_routes = set(df[df['Stop_name'] == destination]['Route_long_name'])
        common_routes = list(orig_routes.intersection(dest_routes))

        if common_routes:
            selected_route = st.selectbox("Select Route Suggestion:", common_routes)
            
            # Get the stop sequence for the selected route
            route_data = df[df['Route_long_name'] == selected_route].drop_duplicates(subset=['Stop_name']).sort_values('Arrival_time')
            
            # Extract the segment between origin and destination
            stops_list = route_data['Stop_name'].tolist()
            try:
                idx_start = stops_list.index(origin)
                idx_end = stops_list.index(destination)
                
                # Handle direction (A to B or B to A)
                if idx_start < idx_end:
                    journey_segment = route_data.iloc[idx_start:idx_end+1]
                else:
                    journey_segment = route_data.iloc[idx_end:idx_start+1][::-1]

                # --- MAP SECTION ---
                st.subheader(f"Route Path: {selected_route}")
                
                view_state = pdk.ViewState(
                    latitude=journey_segment['Stop_lat'].mean(),
                    longitude=journey_segment['Stop_lon'].mean(),
                    zoom=12, pitch=0
                )

                # Path Layer (Lines)
                path_data = [{"path": journey_segment[['Stop_lon', 'Stop_lat']].values.tolist()}]
                
                layers = [
                    pdk.Layer(
                        "PathLayer",
                        path_data,
                        get_color=[128, 128, 0], # Olive Gold
                        width_min_pixels=5,
                    ),
                    pdk.Layer(
                        "ScatterplotLayer",
                        journey_segment,
                        get_position="[Stop_lon, Stop_lat]",
                        get_color=[255, 255, 255],
                        get_radius=100,
                        pickable=True,
                    ),
                ]

                st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=view_state, tooltip={"text": "{Stop_name}"}))

                # --- DIRECTIONS & SENTIMENT SECTION ---
                st.subheader("Step-by-Step Directions & Station Vibe")
                
                for i, (_, row) in enumerate(journey_segment.iterrows()):
                    icon = "🟢" if i == 0 else "🔴" if i == len(journey_segment)-1 else "⚪"
                    with st.expander(f"{icon} Stop {i+1}: {row['Stop_name']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Rating:** {row['avg_rating'] if pd.notnull(row['avg_rating']) else 'N/A'} ⭐")
                        with col2:
                            sentiment = row['main_sentiment'] if pd.notnull(row['main_sentiment']) else "No Data"
                            color = "green" if sentiment == "Positive" else "red" if sentiment == "Negative" else "orange"
                            st.markdown(f"**Sentiment:** :{color}[{sentiment}]")

            except ValueError:
                st.error("Could not determine sequence. Try another route.")
        else:
            st.error("No direct route found.")
else:
    st.info("Select your starting point and destination in the sidebar.")
