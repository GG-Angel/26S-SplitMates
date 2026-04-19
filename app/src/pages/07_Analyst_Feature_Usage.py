import logging
import json
import streamlit as st
import streamlit.components.v1 as components
from api.client import client
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide", page_title="SplitMates | Feature Usage")
SideBarLinks()

audit_logs: list[dict] = client.get("/analyst/audit-logs") or []
audit_activity: list[dict] = client.get("/analyst/audit-logs/activity") or []
sessions: list[dict] = client.get("/analyst/sessions") or []
inactive_users: list[dict] = client.get("/analyst/users/inactive") or []

st.markdown("""
<style>
    .page-subtitle { color: #667085; font-size: 1rem; margin-top: 0; margin-bottom: 1.5rem; }
    h1 { font-size: 2.2rem !important; font-weight: 700 !important; margin-bottom: 0.1rem !important; }
    .metric-card { background: white; border: 1px solid #EAECF0; border-radius: 12px; padding: 1rem 1rem 0.85rem 1rem; box-shadow: 0 1px 2px rgba(16,24,40,0.04); height: 100%; }
    .metric-label { color: #667085; font-size: 0.85rem; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; }
    .metric-value { color: #101828; font-size: 2.4rem; font-weight: 800; line-height: 1; margin-top: 0.15rem; }
    .metric-value-sm { color: #101828; font-size: 1.3rem; font-weight: 800; line-height: 1.2; margin-top: 0.15rem; }
    .metric-note { color: #475467; font-size: 0.85rem; margin-top: 0.45rem; }
</style>""", unsafe_allow_html=True)

st.title("Feature Usage Overview")
st.markdown('<div class="page-subtitle">Track which features and actions are used most across the platform.</div>', unsafe_allow_html=True)

total_actions = sum(r.get("total_uses", 0) for r in audit_logs)
avg_actions = round(total_actions / len(audit_logs), 1) if audit_logs else 0
most_used = (audit_logs[0]["target_table"] + " / " + audit_logs[0]["action_type"]) if audit_logs else "N/A"
most_used_count = audit_logs[0]["total_uses"] if audit_logs else 0
least_used = (audit_logs[-1]["target_table"] + " / " + audit_logs[-1]["action_type"]) if audit_logs else "N/A"
least_used_count = audit_logs[-1]["total_uses"] if audit_logs else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">TOTAL ACTIONS</div><div class="metric-value">{total_actions}</div><div class="metric-note">Across all features</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-label">AVG ACTIONS / FEATURE</div><div class="metric-value">{avg_actions}</div><div class="metric-note">Avg clicks per feature</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-label">MOST USED</div><div class="metric-value-sm">{most_used}</div><div class="metric-note">{most_used_count} clicks</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-label">LEAST USED</div><div class="metric-value-sm">{least_used}</div><div class="metric-note">{least_used_count} click</div></div>', unsafe_allow_html=True)


st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

col_clicks = st.container()

with col_clicks:
    import json as _fj2
    fc_monthly = {
        "All": [("chores / Create",7),("groups / Create",6),("chores / Delete",5),("events / Create",5),("bills / Update",5),("users / Create",3),("items / Delete",3)],
        "Jan": [("chores / Create",3),("groups / Create",2),("events / Create",2),("bills / Update",1),("users / Create",1),("chores / Delete",1),("items / Delete",0)],
        "Feb": [("chores / Create",2),("groups / Create",2),("chores / Delete",2),("bills / Update",2),("events / Create",1),("users / Create",1),("items / Delete",1)],
        "Mar": [("chores / Create",1),("groups / Create",1),("chores / Delete",1),("events / Create",1),("bills / Update",1),("users / Create",1),("items / Delete",2)],
        "Apr": [("chores / Create",1),("groups / Create",1),("events / Create",1),("bills / Update",1),("users / Create",0),("chores / Delete",1),("items / Delete",0)],
    }
    fc_json = {m: {"labels": [f for f,_ in v], "values": [c for _,c in v]} for m,v in fc_monthly.items()}
    fc_month_opts = "".join(("<option value=\"" + m + "\"" + (" selected" if m=="All" else "") + ">" + m + "</option>") for m in fc_json)
    components.html(f"""
    <div style="background:white;border:1px solid #EAECF0;border-radius:12px;padding:1.25rem;box-shadow:0 1px 2px rgba(16,24,40,0.04);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
            <div style="font-size:1.1rem;font-weight:700;color:#101828;font-family:sans-serif;">Feature Clicks</div>
            <select id="fcMonth" style="border:1px solid #EAECF0;border-radius:6px;padding:4px 10px;font-size:0.85rem;color:#101828;">{fc_month_opts}</select>
        </div>
        <div style="position:relative;height:355px;">
            <canvas id="hbarChart" role="img" aria-label="Horizontal bar chart of feature clicks">Feature clicks</canvas>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <script>
    const fcData = {_fj2.dumps(fc_json)};
    const hbar = new Chart(document.getElementById('hbarChart'), {{
        type: 'bar',
        data: {{ labels: fcData['All'].labels, datasets: [{{ data: fcData['All'].values, backgroundColor: '#E31B1B' }}] }},
        options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }} }},
            scales: {{ x: {{ ticks: {{ stepSize: 1, font: {{ size: 10 }}, color: '#101828' }}, grid: {{ color: '#F2F4F7' }}, beginAtZero: true }}, y: {{ ticks: {{ font: {{ size: 10 }}, color: '#101828' }}, grid: {{ display: false }} }} }} }}
    }});
    document.getElementById('fcMonth').addEventListener('change', e => {{
        hbar.data.labels = fcData[e.target.value].labels;
        hbar.data.datasets[0].data = fcData[e.target.value].values;
        hbar.update();
    }});
    </script>""", height=460, scrolling=False)


# ── Chore Completion Trends ────────────────────────────────────────────────────
st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

chores: list[dict] = client.get("/analyst/chores/completed") or []

if chores:
    import json as _cj2
    import streamlit.components.v1 as _cc
    chore_labels = [r["title"] for r in chores]
    chore_values = [r["times_completed"] for r in chores]
    effort_colors = {"low": "#fca5a5", "medium": "#E31B1B", "high": "#7f1d1d"}
    chore_colors = [effort_colors.get(r["effort"], "#6366f1") for r in chores]

    _cc.html(f"""
    <div style="background:white;border:1px solid #EAECF0;border-radius:12px;padding:1.25rem;box-shadow:0 1px 2px rgba(16,24,40,0.04);">
        <div style="font-size:1.1rem;font-weight:700;color:#101828;margin-bottom:0.5rem;font-family:sans-serif;">Chore Completion Trends</div>
        <div style="font-size:0.8rem;color:#667085;margin-bottom:1rem;font-family:sans-serif;">
            <span style="display:inline-flex;align-items:center;gap:4px;margin-right:12px;"><span style="width:10px;height:10px;border-radius:2px;background:#E31B1B;display:inline-block;"></span>Low effort</span>
            <span style="display:inline-flex;align-items:center;gap:4px;margin-right:12px;"><span style="width:10px;height:10px;border-radius:2px;background:#E31B1B;display:inline-block;"></span>Medium effort</span>
            <span style="display:inline-flex;align-items:center;gap:4px;"><span style="width:10px;height:10px;border-radius:2px;background:#E31B1B;display:inline-block;"></span>High effort</span>
        </div>
        <div style="position:relative;height:240px;">
            <canvas id="choreChart" role="img" aria-label="Chore completion trends bar chart">Chore completions</canvas>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <script>
    new Chart(document.getElementById('choreChart'), {{
        type: 'bar',
        data: {{ labels: {_cj2.dumps(chore_labels)}, datasets: [{{ data: {_cj2.dumps(chore_values)}, backgroundColor: {_cj2.dumps(chore_colors)}, borderRadius: 4 }}] }},
        options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }},
            scales: {{ x: {{ ticks: {{ font: {{ size: 11 }}, color: '#101828' }}, grid: {{ display: false }} }}, y: {{ ticks: {{ stepSize: 1, font: {{ size: 11 }}, color: '#101828' }}, grid: {{ color: '#F2F4F7' }}, beginAtZero: true }} }} }}
    }});
    </script>""", height=360, scrolling=False)
