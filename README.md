# ⚽ FPL Algorithm

> *Data-driven FPL decisions*

An interactive Fantasy Premier League analytics dashboard powered by Python and Streamlit. Analyze players based on form, cost, minutes, and upcoming fixture difficulty. Make smarter transfer, captaincy, and squad decisions — all in one place.

![screenshot](FPLAnalyst.PNG) <!-- Replace with your own image later -->

---

## 🚀 Features

- 🏆 Player rankings based on performance & value
- 🔍 Compare players side-by-side
- 📅 Visualize next 5 fixtures and difficulty for any team
- 📥 Download filtered player data as CSV
- 💡 Clean tabbed interface and dynamic filters

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Python)
- **Backend**: Python OOP (`FPLPlayer`, `FPLManager`, `FPLTeam`)
- **Data**: Official [FPL API](https://fantasy.premierleague.com/api/)
- **Libraries**: pandas, requests, streamlit

---

## 💻 Setup Locally

```bash
git clone https://github.com/YOUR_USERNAME/fpl-algorithm.git
cd fpl-algorithm
pip install -r requirements.txt
streamlit run app.py
