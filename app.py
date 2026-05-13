import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Transit Insight - Route Planner", layout="wide")

@st.cache_data
def load_data():
    # Loading the compressed dataset with Stop_search and coordinates
    return pd.read_csv('route_planner_map_data_small.csv')

df = load_data()

st.title("📍 Transit Route & Sentiment Planner")
st.write("Plan your trip using the exact stop names from our transit master and review datasets.")

# Sidebar for Search using 'Stop_search'
st.sidebar.header("Journey Planner")
# User searches using 'Stop_search' as requested
origin_search = st.sidebar.selectbox("Select Origin (Stop Search):", options=[""] + sorted(df['Stop_search'].unique().tolist()))
dest_search = st.sidebar.selectbox("Select Destination (Stop Search):", options=[""] + sorted(df['Stop_search'].unique().tolist()))

if origin_search and dest_search:
    if origin_search == dest_search:
        st.warning("Origin and Destination cannot be the same stop.")
    else:
        # Find shared routes based on the Stop_search column
        origin_routes = set(df[df['Stop_search'] == origin_search]['Route_long_name'])
        dest_routes = set(df[df['Stop_search'] == dest_search]['Route_long_name'])
        common_routes = list(origin_routes.intersection(dest_routes))

        if common_routes:
            selected_route = st.selectbox("Available Route Suggestions:", common_routes)
            
            # Filter data for the specific route to determine stop sequence
            route_data = df[df['Route_long_name'] == selected_route].drop_duplicates(subset=['Stop_search'])
            
            # Create a sequence list for the specific route
            stops_list = route_data['Stop_search'].tolist()
            
            try:
                idx_start = stops_list.index(origin_search)
                idx_end = stops_list.index(dest_search)
                
                # Determine the direction of travel along the route list
                if idx_start < idx_end:
                    journey_segment = route_data.iloc[idx_start:idx_end+1]
                else:
                    journey_segment = route_data.iloc[idx_end:idx_start+1][::-1]

                # --- INTERACTIVE MAP ---
                st.subheader(f"Map View: {selected_route}")
                
                view_state = pdk.ViewState(
                    latitude=journey_segment['Stop_lat'].mean(),
                    longitude=journey_segment['Stop_lon'].mean(),
                    zoom=13, pitch=0
                )

                layers = [
                    pdk.Layer(
                        "PathLayer",
                        [{"path": journey_segment[['Stop_lon', 'Stop_lat']].values.tolist()}],
                        get_color=[128, 128, 0], # Transit Insight Olive Gold
                        width_min_pixels=6,
                    ),
                    pdk.Layer(
                        "ScatterplotLayer",
                        journey_segment,
                        get_position="[Stop_lon, Stop_lat]",
                        get_color=[255, 255, 255],
                        get_radius=80,
                        pickable=True,
                    ),
                ]

                st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=view_state, tooltip={"text": "{Stop_search}"}))

                # --- STEP-BY-STEP DIRECTIONS & SENTIMENT ---
                st.subheader("Journey Steps & Station Sentiment")
                
                for i, (_, row) in enumerate(journey_segment.iterrows()):
                    # Use 'Stop_search' for the display to maintain consistency
                    label = "START" if i == 0 else "END" if i == len(journey_segment)-1 else f"Step {i+1}"
                    with st.expander(f"{label}: {row['Stop_search']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            rating = f"{row['avg_rating']:.1f} ⭐" if pd.notnull(row['avg_rating']) else "No Rating"
                            st.write(f"**Average Rating:** {rating}")
                        with col2:
                            sentiment = row['main_sentiment'] if pd.notnull(row['main_sentiment']) else "No Reviews"
                            color = "green" if sentiment == "Positive" else "red" if sentiment == "Negative" else "orange"
                            st.markdown(f"**Commuter Vibe:** :{color}[{sentiment}]")

            except ValueError:
                st.error("Route sequence error. Please select another suggested route.")
        else:
            st.error("No direct route connects these two 'Stop Search' locations.")
else:
    st.info("Select an Origin and Destination from the sidebar to begin.")
