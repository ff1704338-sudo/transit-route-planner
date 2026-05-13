import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Transit Insight - Comprehensive Route Planner", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('route_planner_map_data_small.csv')

df = load_data()

st.title("📍 Transit Route & Sentiment Planner")

# Sidebar for Search
st.sidebar.header("Journey Planner")
origin_search = st.sidebar.selectbox("Select Origin (Stop Search):", options=[""] + sorted(df['Stop_search'].unique().tolist()))
dest_search = st.sidebar.selectbox("Select Destination (Stop Search):", options=[""] + sorted(df['Stop_search'].unique().tolist()))

if origin_search and dest_search:
    if origin_search == dest_search:
        st.warning("Origin and Destination cannot be the same.")
    else:
        # Find shared routes
        origin_routes = set(df[df['Stop_search'] == origin_search]['Route_long_name'])
        dest_routes = set(df[df['Stop_search'] == dest_search]['Route_long_name'])
        common_routes = list(origin_routes.intersection(dest_routes))

        if common_routes:
            selected_route = st.selectbox("Available Route Suggestions:", common_routes)
            route_data = df[df['Route_long_name'] == selected_route].drop_duplicates(subset=['Stop_search'])
            stops_list = route_data['Stop_search'].tolist()
            
            try:
                idx_start = stops_list.index(origin_search)
                idx_end = stops_list.index(dest_search)
                
                # Get the journey segment
                if idx_start < idx_end:
                    journey_segment = route_data.iloc[idx_start:idx_end+1]
                else:
                    journey_segment = route_data.iloc[idx_end:idx_start+1][::-1]

                # --- OVERALL SUMMARY SECTION ---
                st.subheader("🏁 Overall Journey Summary")
                
                # Calculate averages for the segment
                avg_journey_rating = journey_segment['avg_rating'].mean()
                avg_journey_sentiment = journey_segment['avg_sentiment'].mean()
                
                # Determine category for overall sentiment
                if avg_journey_sentiment > 0.05:
                    overall_cat = "Positive"
                    overall_color = "green"
                elif avg_journey_sentiment < -0.05:
                    overall_cat = "Negative"
                    overall_color = "red"
                else:
                    overall_cat = "Neutral"
                    overall_color = "orange"

                # Display Metrics
                m_col1, m_col2, m_col3 = st.columns(3)
                m_col1.metric("Total Stops", len(journey_segment))
                m_col2.metric("Overall Journey Rating", f"{avg_journey_rating:.2f} / 5.0")
                m_col3.markdown(f"**Overall Sentiment:** <br><span style='font-size:24px; color:{overall_color}; font-weight:bold;'>{overall_cat}</span>", unsafe_allow_html=True)
                
                st.divider()

                # --- MAP VIEW ---
                st.subheader(f"Map View: {selected_route}")
                view_state = pdk.ViewState(
                    latitude=journey_segment['Stop_lat'].mean(),
                    longitude=journey_segment['Stop_lon'].mean(),
                    zoom=13, pitch=0
                )
                layers = [
                    pdk.Layer("PathLayer", [{"path": journey_segment[['Stop_lon', 'Stop_lat']].values.tolist()}],
                              get_color=[128, 128, 0], width_min_pixels=6),
                    pdk.Layer("ScatterplotLayer", journey_segment, get_position="[Stop_lon, Stop_lat]",
                              get_color=[255, 255, 255], get_radius=80, pickable=True),
                ]
                st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=view_state, tooltip={"text": "{Stop_search}"}))

                # --- STEP-BY-STEP DIRECTIONS ---
                st.subheader("Journey Steps & Individual Station Sentiment")
                for i, (_, row) in enumerate(journey_segment.iterrows()):
                    label = "START" if i == 0 else "END" if i == len(journey_segment)-1 else f"Stop {i+1}"
                    with st.expander(f"{label}: {row['Stop_search']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Rating:** {row['avg_rating']:.1f} ⭐" if pd.notnull(row['avg_rating']) else "**Rating:** N/A")
                        with col2:
                            s = row['main_sentiment'] if pd.notnull(row['main_sentiment']) else "No Reviews"
                            c = "green" if s == "Positive" else "red" if s == "Negative" else "orange"
                            st.markdown(f"**Vibe:** :{c}[{s}]")

            except ValueError:
                st.error("Sequence error. Try another route.")
        else:
            st.error("No direct route connects these locations.")
else:
    st.info("Select Origin and Destination in the sidebar.")
