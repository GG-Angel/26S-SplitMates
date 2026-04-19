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

# Build stacked bar data from audit logs
from collections import defaultdict
import json as _cj

table_actions = defaultdict(lambda: {"create": 0, "update": 0, "delete": 0})
for r in audit_logs:
    table_actions[r["target_table"]][r["action_type"]] += r.get("total_uses", 0)

# Sort by total
sorted_tables = sorted(table_actions.items(), key=lambda x: sum(x[1].values()), reverse=True)
tables = [t for t,_ in sorted_tables]
creates = [table_actions[t]["create"] for t in tables]
updates = [table_actions[t]["update"] for t in tables]
deletes = [table_actions[t]["delete"] for t in tables]

# Action type totals for simple bar
action_totals = {"create": 0, "update": 0, "delete": 0}
for r in audit_logs:
    action_totals[r["action_type"]] += r.get("total_uses", 0)

col_stack, col_action = st.columns(2, gap="large")

with col_stack:
    components.html(f"""
    <div style="background:white;border:1px solid #EAECF0;border-radius:12px;padding:1.25rem;box-shadow:0 1px 2px rgba(16,24,40,0.04);">
        <div style="font-size:1.1rem;font-weight:700;color:#101828;margin-bottom:0.5rem;font-family:sans-serif;">Feature Activity by Action Type</div>
        <div style="position:relative;height:280px;">
            <canvas id="stackChart" role="img" aria-label="Stacked bar chart of feature activity by action type">Feature breakdown</canvas>
        </div>
        <div style="display:flex;gap:16px;margin-top:8px;font-size:11px;font-family:sans-serif;">
            <span style="display:flex;align-items:center;gap:4px;"><span style="width:10px;height:10px;border-radius:2px;background:#6366f1;display:inline-block;"></span>Create</span>
            <span style="display:flex;align-items:center;gap:4px;"><span style="width:10px;height:10px;border-radius:2px;background:#f59e0b;display:inline-block;"></span>Update</span>
            <span style="display:flex;align-items:center;gap:4px;"><span style="width:10px;height:10px;border-radius:2px;background:#E31B1B;display:inline-block;"></span>Delete</span>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <script>
    new Chart(document.getElementById('stackChart'), {{
        type: 'bar',
        data: {{
            labels: {_cj.dumps(tables)},
            datasets: [
                {{ label: 'Create', data: {_cj.dumps(creates)}, backgroundColor: '#6366f1' }},
                {{ label: 'Update', data: {_cj.dumps(updates)}, backgroundColor: '#f59e0b' }},
                {{ label: 'Delete', data: {_cj.dumps(deletes)}, backgroundColor: '#E31B1B' }}
            ]
        }},
        options: {{
            responsive: true, maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }} }},
            scales: {{
                x: {{ stacked: true, ticks: {{ font: {{ size: 10 }}, color: '#101828' }}, grid: {{ display: false }} }},
                y: {{ stacked: true, ticks: {{ stepSize: 1, font: {{ size: 10 }}, color: '#101828' }}, grid: {{ color: '#F2F4F7' }}, beginAtZero: true }}
            }}
        }}
    }});
    </script>""", height=360, scrolling=False)

with col_action:
    action_labels = list(action_totals.keys())
    action_values = list(action_totals.values())
    action_colors = ['#6366f1', '#f59e0b', '#E31B1B']
    components.html(f"""
    <div style="background:white;border:1px solid #EAECF0;border-radius:12px;padding:1.25rem;box-shadow:0 1px 2px rgba(16,24,40,0.04);">
        <div style="font-size:1.1rem;font-weight:700;color:#101828;margin-bottom:0.5rem;font-family:sans-serif;">Actions by Type</div>
        <div style="position:relative;height:280px;">
            <canvas id="actionChart" role="img" aria-label="Bar chart of total actions by type">Action totals</canvas>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <script>
    new Chart(document.getElementById('actionChart'), {{
        type: 'bar',
        data: {{
            labels: {_cj.dumps([a.title() for a in action_labels])},
            datasets: [{{ data: {_cj.dumps(action_values)}, backgroundColor: ['#E31B1B','#E31B1B','#E31B1B'], borderRadius: 4 }}]
        }},
        options: {{
            responsive: true, maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }} }},
            scales: {{
                x: {{ ticks: {{ font: {{ size: 12 }}, color: '#101828' }}, grid: {{ display: false }} }},
                y: {{ ticks: {{ stepSize: 2, font: {{ size: 11 }}, color: '#101828' }}, grid: {{ color: '#F2F4F7' }}, beginAtZero: true }}
            }}
        }}
    }});
    </script>""", height=360, scrolling=False)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

import json as _fj
from collections import defaultdict as _dd

col_clicks, col_top5 = st.columns(2, gap="large")

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

with col_top5:
    t5_monthly = {
        "All": [("chores",12),("groups",10),("events",9),("bills",9),("sessions",8)],
        "Jan": [("chores",4),("groups",3),("bills",3),("events",2),("items",2)],
        "Feb": [("groups",3),("chores",3),("events",3),("sessions",2),("bills",2)],
        "Mar": [("chores",3),("events",2),("bills",2),("sessions",2),("users",2)],
        "Apr": [("chores",2),("groups",2),("bills",2),("events",2),("sessions",2)],
    }
    import json as _fj
    t5_json = {m: {"labels": [t for t,_ in v], "values": [c for _,c in v]} for m,v in t5_monthly.items()}
    t5_month_opts = "".join(("<option value=\"" + m + "\"" + (" selected" if m=="All" else "") + ">" + m + "</option>") for m in t5_json)
    components.html(f"""
    <div style="background:white;border:1px solid #EAECF0;border-radius:12px;padding:1.25rem;box-shadow:0 1px 2px rgba(16,24,40,0.04);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
            <div style="font-size:1.1rem;font-weight:700;color:#101828;font-family:sans-serif;">Top 5 Most Active Tables</div>
            <select id="t5Month" style="border:1px solid #EAECF0;border-radius:6px;padding:4px 10px;font-size:0.85rem;color:#101828;">{t5_month_opts}</select>
        </div>
        <div style="position:relative;height:355px;"><canvas id="top5Chart" role="img" aria-label="Top 5 most active tables">Table activity</canvas></div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <script>
    const t5Data = {_fj.dumps(t5_json)};
    const t5bar = new Chart(document.getElementById('top5Chart'), {{
        type: 'bar',
        data: {{ labels: t5Data['All'].labels, datasets: [{{ data: t5Data['All'].values, backgroundColor: '#E31B1B', borderRadius: 4 }}] }},
        options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }},
            scales: {{ x: {{ ticks: {{ font: {{ size: 11 }}, color: '#101828' }}, grid: {{ display: false }} }}, y: {{ ticks: {{ stepSize: 1, font: {{ size: 11 }}, color: '#101828' }}, grid: {{ color: '#F2F4F7' }}, beginAtZero: true }} }} }}
    }});
    document.getElementById('t5Month').addEventListener('change', e => {{
        t5bar.data.labels = t5Data[e.target.value].labels;
        t5bar.data.datasets[0].data = t5Data[e.target.value].values;
        t5bar.update();
    }});
    </script>""", height=460, scrolling=False)

