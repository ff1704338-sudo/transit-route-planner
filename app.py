import streamlit as st
import pandas as pd

# Set page configuration for a professional look
st.set_page_config(page_title="Transit Insight - Route Planner", layout="wide")

# Load the processed data
@st.cache_data
def load_data():
    return pd.read_csv('route_planner_data.csv')

df = load_data()

# Custom CSS to match your "Transit Insight" theme (Olive/Gold)
st.markdown("""
    <style>
    .main { background-color: #f5f5dc; }
    .stButton>button { background-color: #808000; color: white; }
    .sentiment-pos { color: green; font-weight: bold; }
    .sentiment-neg { color: red; font-weight: bold; }
    .sentiment-neu { color: #808000; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True) # Corrected parameter name

st.title("📍 Transit Route & Sentiment Planner")
st.write("Search for a stop to find available routes and see commuter feedback.")

# Search interface
search_query = st.selectbox("Select or type a Stop Name:", options=[""] + sorted(df['Stop_search'].unique().tolist()))

if search_query:
    results = df[df['Stop_search'] == search_query]
    
    st.subheader(f"Routes passing through: {search_query}")
    
    for index, row in results.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"### 🚆 {row['Route_long_name']}")
                st.write(f"**Type:** {row['Transport_type']}")
            
            with col2:
                # Handle missing rating data
                rating = f"{row['avg_rating']:.1f} / 5.0" if pd.notnull(row['avg_rating']) else "No Rating"
                st.metric("Avg Rating", rating)
                
            with col3:
                # Sentiment Badge
                sentiment = row['main_sentiment'] if pd.notnull(row['main_sentiment']) else "No Data"
                if sentiment == "Positive":
                    st.markdown(f"Sentiment: <span class='sentiment-pos'>{sentiment}</span>", unsafe_allow_html=True)
                elif sentiment == "Negative":
                    st.markdown(f"Sentiment: <span class='sentiment-neg'>{sentiment}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"Sentiment: <span class='sentiment-neu'>{sentiment}</span>", unsafe_allow_html=True)
            
            st.divider()
else:
    st.info("Please select a stop to see the route details.")
