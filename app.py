import datetime

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

    /* Sidebar selectbox: force text inside the box to black */
    section[data-testid="stSidebar"] .stSelectbox div,
    section[data-testid="stSidebar"] .stSelectbox span,
    section[data-testid="stSidebar"] .stSelectbox p {
        color: #000000 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* Hide the original (broken) dropdown icon entirely */
    section[data-testid="stSidebar"] .stSelectbox svg,
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] svg,
    section[data-testid="stSidebar"] .stSelectbox svg * {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
    }

    /* In case the icon is a background/mask div rather than an svg, strip its background too */
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div:last-child {
        background: transparent !important;
        background-image: none !important;
        background-color: transparent !important;
    }
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        position: relative;
    }
    section[data-testid="stSidebar"] .stSelectbox > div > div::after {
        content: "";
        position: absolute;
        right: 16px;
        top: 50%;
        width: 0;
        height: 0;
        transform: translateY(-50%);
        border-left: 6px solid transparent;
        border-right: 6px solid transparent;
        border-top: 7px solid #14213D;
        pointer-events: none;
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

    /* Expander header text -> white (covers current Streamlit DOM: details/summary structure) */
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary div,
    [data-testid="stExpanderToggleIcon"],
    [data-testid="stExpander"] svg {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        opacity: 1 !important;
    }

    /* Expander header (collapsed box) -> black background so white text is visible */
    [data-testid="stExpander"] summary {
        background-color: #000000 !important;
        border-radius: 8px;
        padding: 8px 14px !important;
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


def _time_to_minutes(t):
    """Convert an 'H:MM:SS' / 'HH:MM:SS' string (hours may exceed 24 for
    past-midnight trips) into minutes-since-midnight (float)."""
    h, m, s = str(t).split(':')
    return int(h) * 60 + int(m) + int(s) / 60


@st.cache_data
def load_data():
    # Trip-level data: every row is one stop on one specific scheduled trip,
    # already in the correct sequential order for that trip (stop_seq).
    # This is what lets us build a journey that never doubles back -
    # we always slice a single real Trip_id rather than stitching together
    # stops that happen to share a name across different trips/directions.
    data = pd.read_csv('route_planner_trips.csv', low_memory=False)
    data['_minutes'] = data['Arrival_time'].apply(_time_to_minutes)
    return data

df = load_data()

st.title("📍 Transit Route & Sentiment Planner")

# --- Sidebar: Journey Planner ---
st.sidebar.header("Journey Planner")

all_stops = sorted(df['Stop_search'].unique().tolist())
origin_search = st.sidebar.selectbox("Select Origin:", options=[""] + all_stops)
dest_search = st.sidebar.selectbox("Select Destination:", options=[""] + all_stops)

service_day_options = {
    "Weekday (Mon-Fri)": "Weekday",
    "Weekend / Holiday": "Weekend/Holiday",
}
service_day_label = st.sidebar.selectbox("Travel Day:", options=list(service_day_options.keys()))
service_day = service_day_options[service_day_label]

time_slot_options = [f"{h:02d}:{m:02d}" for h in range(24) for m in range(60)]
selected_time_str = st.sidebar.selectbox(
    "Preferred Departure Time:",
    options=time_slot_options,
    index=None,
    placeholder="Choose a preferred time",
)
if selected_time_str:
    _hh, _mm = map(int, selected_time_str.split(':'))
    desired_time = datetime.time(_hh, _mm)
else:
    # No preference chosen yet - fall back to a neutral default (10:00)
    # purely for the "closest departure" sorting math below.
    desired_time = datetime.time(10, 0)
desired_minutes = desired_time.hour * 60 + desired_time.minute

if origin_search and dest_search:
    if origin_search == dest_search:
        st.warning("Origin and Destination cannot be the same.")
    else:
        # --- Find every scheduled trip (on the chosen day) that actually
        # visits the origin BEFORE the destination in its own stop
        # sequence. This guarantees the journey travels in one direction
        # and never backtracks through a stop it already passed. ---
        day_df = df[df['Service_Days'] == service_day]

        origin_rows = day_df[day_df['Stop_search'] == origin_search][
            ['Trip_id', 'stop_seq', '_minutes', 'Route_long_name']
        ].rename(columns={'stop_seq': 'o_seq', '_minutes': 'o_min'})

        dest_rows = day_df[day_df['Stop_search'] == dest_search][
            ['Trip_id', 'stop_seq']
        ].rename(columns={'stop_seq': 'd_seq'})

        candidates = origin_rows.merge(dest_rows, on='Trip_id')
        candidates = candidates[candidates['o_seq'] < candidates['d_seq']]

        if candidates.empty:
            st.error(
                f"No direct route connects these locations on a "
                f"{service_day_label.lower()}. Try the other travel day, "
                f"or a different origin/destination."
            )
        else:
            # Circular time distance so 11:55pm vs 12:05am is "10 min", not ~1430.
            raw_diff = (candidates['o_min'] - desired_minutes) % 1440
            candidates = candidates.copy()
            candidates['diff'] = raw_diff.apply(lambda x: min(x, 1440 - x))

            # Best (closest-to-preferred-time) trip per available route
            best_idx = candidates.groupby('Route_long_name')['diff'].idxmin()
            best_per_route = candidates.loc[best_idx].sort_values('diff')

            def fmt_hm(total_minutes):
                total_minutes = int(round(total_minutes)) % 1440
                return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"

            route_options = []
            route_label_map = {}
            for _, r in best_per_route.iterrows():
                label = f"{r['Route_long_name']} — departs {fmt_hm(r['o_min'])} ({int(r['diff'])} min from preferred time)"
                route_options.append(label)
                route_label_map[label] = r

            selected_label = st.selectbox("Available Route Suggestions:", route_options)
            chosen = route_label_map[selected_label]
            selected_route = chosen['Route_long_name']
            trip_id = chosen['Trip_id']
            o_seq, d_seq = chosen['o_seq'], chosen['d_seq']

            # Slice the ONE real trip's own rows, in order - this is what
            # fixes the old bug where the map could jump back to an
            # already-visited stop.
            journey_segment = (
                df[(df['Trip_id'] == trip_id) & (df['stop_seq'] >= o_seq) & (df['stop_seq'] <= d_seq)]
                .sort_values('stop_seq')
                .reset_index(drop=True)
            )

            # --- OVERALL SUMMARY SECTION ---
            st.subheader("🏁 Overall Journey Summary")

            avg_journey_rating = journey_segment['avg_rating'].mean()
            avg_journey_sentiment = journey_segment['avg_sentiment'].mean()

            if pd.notnull(avg_journey_sentiment) and avg_journey_sentiment > 0.05:
                overall_cat = "Positive"
                overall_color = "#2E6F40"
            elif pd.notnull(avg_journey_sentiment) and avg_journey_sentiment < -0.05:
                overall_cat = "Negative"
                overall_color = "#A94442"
            else:
                overall_cat = "Neutral"
                overall_color = "#C38D39"

            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("Total Stops", len(journey_segment))
            m_col2.metric(
                "Overall Journey Rating",
                f"{avg_journey_rating:.2f} / 5.0" if pd.notnull(avg_journey_rating) else "N/A"
            )
            m_col3.metric("Departs", fmt_hm(chosen['o_min']), f"{int(chosen['diff'])} min from preferred")
            m_col4.markdown(
                f"""
                <div style='background-color:#FFFFFF; border:1px solid #E3D5C6; border-radius:10px;
                            padding:16px 18px; box-shadow: 0 2px 6px rgba(74, 62, 61, 0.08);'>
                    <span style='color:#14213D; font-weight:600; font-size:14px;'>Overall Sentiment</span><br>
                    <span style='font-size:24px; color:{overall_color}; font-weight:800;'>{overall_cat}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.caption(
                f"Showing the {service_day_label.lower()} trip on **{selected_route}** closest to your "
                f"preferred time of {desired_time.strftime('%H:%M')}."
            )

            st.divider()

            # --- MAP VIEW ---
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
                    get_color=[173, 139, 106],
                    width_min_pixels=6
                ),
                pdk.Layer(
                    "ScatterplotLayer",
                    journey_segment,
                    get_position="[Stop_lon, Stop_lat]",
                    get_color=[251, 246, 240],
                    get_line_color=[20, 33, 61],
                    stroked=True,
                    get_radius=80,
                    pickable=True
                ),
            ]
            st.pydeck_chart(pdk.Deck(
                map_provider="carto",
                map_style="light",
                layers=layers,
                initial_view_state=view_state,
                tooltip={"text": "{Stop_search}\n{Arrival_time}"}
            ))

            # --- STEP-BY-STEP DIRECTIONS ---
            st.subheader("Journey Steps & Individual Station Sentiment")
            for i, (_, row) in enumerate(journey_segment.iterrows()):
                label = "START" if i == 0 else "END" if i == len(journey_segment) - 1 else f"Stop {i+1}"
                with st.expander(f"{label}: {row['Stop_search']}  •  {row['Arrival_time']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Rating:** {row['avg_rating']:.1f} ⭐" if pd.notnull(row['avg_rating']) else "**Rating:** N/A")
                    with col2:
                        s = row['main_sentiment'] if pd.notnull(row['main_sentiment']) else "No Reviews"
                        c = "green" if s == "Positive" else "red" if s == "Negative" else "orange"
                        st.markdown(f"**Vibe:** :{c}[{s}]")
else:
    st.info("Select Origin and Destination in the sidebar.")
