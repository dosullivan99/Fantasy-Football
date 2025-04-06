import streamlit as st
import pandas as pd
from FPLPlayer import FPLManager  # Your class-based logic

st.set_page_config(page_title="FPL Optimizer", layout="wide")

# === Load data through your FPLManager ===
@st.cache_data
def load_data():
    manager = FPLManager()
    manager.fetch_all_data()
    return manager

manager = load_data()
with st.container():
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='font-size: 3em;'>⚽ FPL Algorithm</h1>
            <p style='font-size: 1.3em; color: gray; margin-top: -1em;'>Data-driven FPL decisions</p>
            <p style='font-size: 1.1em;'>Built by <strong>Daire O'Sullivan</strong></p>
        </div>
    """, unsafe_allow_html=True)

players = manager.players  # List of FPLPlayer objects

# Convert player list to DataFrame
df = pd.DataFrame([p.to_dict() for p in players])
position_map = {1: "Goalkeeper", 2: "Defender", 3: "Midfielder", 4: "Forward"}
df["position"] = df["position"].map(position_map)
df["team_name"] = df["team_id"].map(manager.team_id_to_name)

# === Tabs ===
tab1, tab2, tab3 = st.tabs(["🏆 Rankings", "🔍 Compare Players", "📅 Fixtures"])

# === 🏆 Tab 1: Rankings ===
with tab1:
    st.title("🏆 FPL Player Optimizer")
    st.markdown("Analyze FPL players based on form, value, minutes, and fixtures.")

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_position = st.selectbox("Filter by Position", ["All"] + sorted(df['position'].unique()))
    with col2:
        selected_team = st.selectbox("Filter by Team", ["All"] + sorted(df['team_name'].unique()))
    with col3:
        max_price = st.slider("Max Price (millions)", 3.5, 15.0, 15.0, 0.1)

    filtered_df = df.copy()
    if selected_position != "All":
        filtered_df = filtered_df[filtered_df['position'] == selected_position]
    if selected_team != "All":
        filtered_df = filtered_df[filtered_df['team_name'] == selected_team]
    filtered_df = filtered_df[filtered_df['cost'] <= max_price]

    sort_option = st.selectbox("Sort By", ["adjusted_score", "value_score", "form", "ppg"])
    filtered_df = filtered_df.sort_values(by=sort_option, ascending=False)

    st.dataframe(
        filtered_df[[
            'name', 'position', 'team_name', 'cost', 'form',
            'ppg', 'minutes', 'value_score', 'adjusted_score'
        ]].reset_index(drop=True),
        use_container_width=True
    )

    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", data=csv, file_name="fpl_rankings.csv", mime='text/csv')

# === 🔍 Tab 2: Compare Players ===
with tab2:
    st.title("🔍 Compare Players")
    player_names = [p.to_dict()["name"] for p in players]

    player1 = st.selectbox("Select Player 1", player_names)
    player2 = st.selectbox("Select Player 2", player_names, index=1)

    p1 = manager.get_player_by_name(player1)
    p2 = manager.get_player_by_name(player2)

    compare_df = pd.DataFrame({
        'Stat': ['Team', 'Position', 'Price', 'Form', 'PPG', 'Minutes', 'Value Score', 'Adjusted Score'],
        player1: [
            manager.team_id_to_name[p1.team_id], position_map[p1.element_type], p1.now_cost, p1.form,
            p1.ppg, p1.minutes, round(p1.value_score, 3), round(p1.adjusted_score, 3)
        ],
        player2: [
            manager.team_id_to_name[p2.team_id], position_map[p2.element_type], p2.now_cost, p2.form,
            p2.ppg, p2.minutes, round(p2.value_score, 3), round(p2.adjusted_score, 3)
        ]
    })

    st.dataframe(compare_df, use_container_width=True)

# === 📅 Tab 3: Fixtures ===
with tab3:
    st.title("📅 Team Fixture Difficulty (Next 5 GWs)")

    team_select = st.selectbox("Select Team", sorted(set(manager.team_id_to_name.values())))
    team_id = next(tid for tid, name in manager.team_id_to_name.items() if name == team_select)
    fixtures = manager.teams[team_id].next_fixtures()

    fixture_df = pd.DataFrame(fixtures)
    fixture_df.columns = ['Gameweek', 'Opponent', 'Difficulty']

    st.table(fixture_df)
