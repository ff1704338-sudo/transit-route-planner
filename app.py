import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Transit Insight - Comprehensive Route Planner", layout="wide")

# --- TRANSIT INSIGHT BRAND THEME CUSTOMIZATION ---
st.markdown("""
    <style>
    /* ---------- Palette ----------
       Cream background : #F4EBE1
       Taupe/brown accent: #AD8B6A / #8C7355
       Dark navy heading : #14213D
       Body text         : #3B3B3B
    ------------------------------- */

    /* Main app background (Cream) and default text */
    .stApp {
        background-color: #F4EBE1;
        color: #3B3B3B;
    }

    /* Sidebar styling - matches header taupe from site nav */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #AD8B6A 0%, #9C7C5C 100%) !important;
        border-right: 1px solid #8C7355;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: #FBF6F0 !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        letter-spacing: 0.5px;
    }
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #F4EBE1 !important;
        border-radius: 6px;
        border: 1px solid #7A6250;
    }

    /* Sidebar selectbox: default placeholder text + selected value text -> black/navy */
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] div,
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span {
        color: #14213D !important;
    }

    /* Sidebar selectbox: dropdown arrow icon -> black/navy */
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] svg {
        fill: #14213D !important;
        color: #14213D !important;
    }

    /* Headings - dark navy, matching hero title on the homepage */
    h1, h2, h3, h4, h5, h6 {
        color: #14213D !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 800;
        letter-spacing: 0.5px;
    }

    /* Main page title styled like the homepage hero */
    h1 {
        text-transform: uppercase;
        border-bottom: 4px solid #AD8B6A;
        padding-bottom: 12px;
        margin-bottom: 24px;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E3D5C6;
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 2px 6px rgba(74, 62, 61, 0.08);
    }
    [data-testid="stMetricValue"] {
        color: #8C7355 !important;
        font-weight: 700;
    }
    [data-testid="stMetricLabel"] {
        color: #14213D !important;
        font-weight: 600;
    }

    /* Expanders styled as clean route-step cards */
    .streamlit-expanderHeader {
        background-color: #FFFFFF !important;
        color: #14213D !important;
        border: 1px solid #E3D5C6 !important;
        border-radius: 8px;
        font-weight: 600;
    }
    .streamlit-expanderContent {
        background-color: #FBF6F0 !important;
        border: 1px solid #E3D5C6 !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px;
    }

    /* Buttons / selects styled with brand brown */
    .stButton>button {
        background-color: #8C7355;
        color: #FBF6F0;
        border-radius: 6px;
        border: none;
        padding: 8px 20px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .stButton>button:hover {
        background-color: #6F5A41;
        color: #FBF6F0;
    }

    /* Divider tint */
    hr {
        border-color: #D9C7B4 !important;
    }

    /* Info / warning / error boxes softened to match palette */
    div[data-testid="stAlert"],
    div[data-testid="stAlert"] * {
        background-color: transparent !important;
    }
    div[data-testid="stAlert"] {
        background-color: #E6DCD2 !important;
        border: 1px solid #C9B399 !important;
        border-radius: 8px;
        padding: 16px 20px !important;
    }
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] span {
        color: #14213D !important;
    }
    div[data-testid="stAlert"] svg {
        fill: #8C7355 !important;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    # Placeholder: Replace with your actual file pathway
    return pd.read_csv('route_planner_map_data_small.csv')

df = load_data()

st.title("📍 Transit Route & Sentiment Planner")

# Sidebar for Search
st.sidebar.header("Journey Planner")
origin_search = st.sidebar.selectbox("Select Origin:", options=[""] + sorted(df['Stop_search'].unique().tolist()))
dest_search = st.sidebar.selectbox("Select Destination:", options=[""] + sorted(df['Stop_search'].unique().tolist()))

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

                # Determine category for overall sentiment (kept legible against cream/navy theme)
                if avg_journey_sentiment > 0.05:
                    overall_cat = "Positive"
                    overall_color = "#2E6F40"  # Soft forest green
                elif avg_journey_sentiment < -0.05:
                    overall_cat = "Negative"
                    overall_color = "#A94442"  # Muted deep red
                else:
                    overall_cat = "Neutral"
                    overall_color = "#C38D39"  # Warm amber/ochre

                # Display Metrics
                m_col1, m_col2, m_col3 = st.columns(3)
                m_col1.metric("Total Stops", len(journey_segment))
                m_col2.metric("Overall Journey Rating", f"{avg_journey_rating:.2f} / 5.0")
                m_col3.markdown(
                    f"""
                    <div style='background-color:#FFFFFF; border:1px solid #E3D5C6; border-radius:10px;
                                padding:16px 18px; box-shadow: 0 2px 6px rgba(74, 62, 61, 0.08);'>
                        <span style='color:#14213D; font-weight:600; font-size:14px;'>Overall Sentiment</span><br>
                        <span style='font-size:24px; color:{overall_color}; font-weight:800;'>{overall_cat}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.divider()

                # --- MAP VIEW ---
                st.subheader(f"Map View: {selected_route}")
                view_state = pdk.ViewState(
                    latitude=journey_segment['Stop_lat'].mean(),
                    longitude=journey_segment['Stop_lon'].mean(),
                    zoom=13, pitch=0
                )

                # Pydeck layers themed to match the website (brown paths, cream/white stop points)
                layers = [
                    pdk.Layer(
                        "PathLayer",
                        [{"path": journey_segment[['Stop_lon', 'Stop_lat']].values.tolist()}],
                        get_color=[173, 139, 106],  # Taupe accent, matches nav bar
                        width_min_pixels=6
                    ),
                    pdk.Layer(
                        "ScatterplotLayer",
                        journey_segment,
                        get_position="[Stop_lon, Stop_lat]",
                        get_color=[251, 246, 240],  # Cream inner color
                        get_line_color=[20, 33, 61],  # Navy border stroke, matches hero heading
                        stroked=True,
                        get_radius=80,
                        pickable=True
                    ),
                ]
                st.pydeck_chart(pdk.Deck(
                    map_style="mapbox://styles/mapbox/light-v10",
                    layers=layers,
                    initial_view_state=view_state,
                    tooltip={"text": "{Stop_search}"}
                ))

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
