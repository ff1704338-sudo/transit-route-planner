import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Transit Insight - Origin/Destination Planner", layout="wide")

# Load the data we created earlier
@st.cache_data
def load_data():
    # This file contains the link between stops, routes, and sentiment
    return pd.read_csv('route_planner_data.csv')

df = load_data()

# Custom CSS for the "Transit Insight" theme
st.markdown("""
    <style>
    .main { background-color: #f5f5dc; }
    .stButton>button { background-color: #808000; color: white; width: 100%; }
    .route-card { background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #808000; margin-bottom: 20px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    .sentiment-pos { color: #28a745; font-weight: bold; }
    .sentiment-neg { color: #dc3545; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🗺️ Transit Route & Sentiment Planner")
st.write("Enter your origin and destination to find the best route and check station quality.")

# Search Layout
col_a, col_b = st.columns(2)
with col_a:
    origin = st.selectbox("Select Origin Stop:", options=[""] + sorted(df['Stop_search'].unique().tolist()))
with col_b:
    destination = st.selectbox("Select Destination Stop:", options=[""] + sorted(df['Stop_search'].unique().tolist()))

if origin and destination:
    if origin == destination:
        st.warning("Origin and destination cannot be the same.")
    else:
        # Find routes that pass through the origin
        origin_routes = set(df[df['Stop_search'] == origin]['Route_long_name'])
        # Find routes that pass through the destination
        dest_routes = set(df[df['Stop_search'] == destination]['Route_long_name'])
        
        # Find the intersection (routes that have both)
        common_routes = origin_routes.intersection(dest_routes)
        
        if common_routes:
            st.subheader(f"Found {len(common_routes)} Suggestion(s)")
            
            for route in common_routes:
                # Get route details
                route_info = df[df['Route_long_name'] == route].iloc[0]
                
                # Get Sentiment for Origin
                orig_data = df[(df['Stop_search'] == origin) & (df['Route_long_name'] == route)].iloc[0]
                # Get Sentiment for Destination
                dest_data = df[(df['Stop_search'] == destination) & (df['Route_long_name'] == route)].iloc[0]
                
                # Display Route Card
                st.markdown(f"""
                <div class="route-card">
                    <h3 style='margin:0;'>🚆 {route}</h3>
                    <p style='color:gray;'>Transport Mode: {route_info['Transport_type']}</p>
                    <hr>
                    <div style='display: flex; justify-content: space-between;'>
                        <div>
                            <strong>Start: {origin}</strong><br>
                            ⭐ Rating: {orig_data['avg_rating'] if pd.notnull(orig_data['avg_rating']) else 'N/A'}/5.0<br>
                            Vibe: <span class='{"sentiment-pos" if orig_data["main_sentiment"] == "Positive" else "sentiment-neg" if orig_data["main_sentiment"] == "Negative" else ""}'>{orig_data['main_sentiment']}</span>
                        </div>
                        <div style='text-align: right;'>
                            <strong>End: {destination}</strong><br>
                            ⭐ Rating: {dest_data['avg_rating'] if pd.notnull(dest_data['avg_rating']) else 'N/A'}/5.0<br>
                            Vibe: <span class='{"sentiment-pos" if dest_data["main_sentiment"] == "Positive" else "sentiment-neg" if dest_data["main_sentiment"] == "Negative" else ""}'>{dest_data['main_sentiment']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("No direct routes found between these two stops. Please try another destination.")
else:
    st.info("Select both an origin and a destination to see route suggestions.")
