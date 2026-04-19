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
                {{ label: 'Create', data: {_cj.dumps(creates)}, backgroundColor: '#6366f1', borderRadius: 2 }},
                {{ label: 'Update', data: {_cj.dumps(updates)}, backgroundColor: '#f59e0b', borderRadius: 2 }},
                {{ label: 'Delete', data: {_cj.dumps(deletes)}, backgroundColor: '#E31B1B', borderRadius: 2 }}
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
            datasets: [{{ data: {_cj.dumps(action_values)}, backgroundColor: {_cj.dumps(action_colors)}, borderRadius: 4 }}]
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

left_col, right_col = st.columns(2, gap="large")

with left_col:
    if audit_logs:
        labels = [f"{r['target_table']} / {r['action_type']}" for r in audit_logs[:10]]
        values = [r["total_uses"] for r in audit_logs[:10]]
        max_v = max(values) if values else 1
        bars = "".join(f"""
        <div style="margin-bottom:0.7rem;">
            <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                <span style="font-size:0.88rem;color:#101828;font-weight:500;">{lbl}</span>
                <span style="font-size:0.88rem;font-weight:700;color:#bd0b0b;">{val}</span>
            </div>
            <div style="background:#F2F4F7;border-radius:4px;height:9px;">
                <div style="background:#E31B1B;border-radius:4px;height:9px;width:{round((val/max_v)*100)}%;"></div>
            </div>
        </div>""" for lbl, val in zip(labels, values))
        components.html(f"""
        <div style="background:white;border:1px solid #EAECF0;border-radius:12px;padding:1.25rem;box-shadow:0 1px 2px rgba(16,24,40,0.04);font-family:'Source Sans Pro',sans-serif;">
            <div style="font-size:1.1rem;font-weight:700;color:#101828;margin-bottom:1rem;">Audit Log Activity</div>
            {bars}
        </div>""", height=80 + len(audit_logs[:10]) * 52, scrolling=False)

with right_col:
    feature_clicks = [("chores / Create",7),("groups / Create",6),("chores / Delete",5),("events / Create",5),("bills / Update",5),("users / Create",3),("items / Delete",3)]
    max_val = max(c for _,c in feature_clicks)
    bars_html = "".join(f"""
    <div style="margin-bottom:0.85rem;">
        <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
            <span style="font-weight:600;font-size:0.9rem;color:#101828;">{lbl}</span>
            <span style="font-weight:700;font-size:0.9rem;color:#bd0b0b;">{cnt}</span>
        </div>
        <div style="background:#F2F4F7;border-radius:4px;height:10px;">
            <div style="background:#E31B1B;border-radius:4px;height:10px;width:{round((cnt/max_val)*100)}%;"></div>
        </div>
    </div>""" for lbl,cnt in feature_clicks)
    components.html(f"""
    <div style="background:white;border:1px solid #EAECF0;border-radius:12px;padding:1.25rem;box-shadow:0 1px 2px rgba(16,24,40,0.04);font-family:'Source Sans Pro',sans-serif;">
        <div style="font-size:1.1rem;font-weight:700;color:#101828;margin-bottom:1rem;">Feature Clicks</div>
        {bars_html}
    </div>""", height=60 + len(feature_clicks)*58, scrolling=False)

st.markdown("<br>", unsafe_allow_html=True)

col_line, col_traffic = st.columns(2, gap="large")

with col_line:
    if audit_activity:
        dates = [r["date"][:16] for r in audit_activity]
        acts = [r["actions"] for r in audit_activity]
        components.html(f"""
        <div style="background:white;border:1px solid #EAECF0;border-radius:12px;padding:1.25rem;box-shadow:0 1px 2px rgba(16,24,40,0.04);">
            <div style="font-size:1.1rem;font-weight:700;color:#101828;margin-bottom:1rem;font-family:'Source Sans Pro',sans-serif;">Platform Activity Over Time</div>
            <div style="position:relative;height:240px;">
                <canvas id="lineChart" role="img" aria-label="Platform activity over time line chart">Activity trend Jan-Apr 2026</canvas>
            </div>
        </div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
        <script>
        new Chart(document.getElementById('lineChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(dates)},
                datasets: [{{
                    data: {json.dumps(acts)},
                    borderColor: '#E31B1B',
                    backgroundColor: 'rgba(227,27,27,0.08)',
                    borderWidth: 2, pointRadius: 2, tension: 0.3, fill: true
                }}]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ ticks: {{ maxRotation: 45, autoSkip: true, maxTicksLimit: 8, font: {{ size: 10 }}, color: '#101828' }}, grid: {{ display: false }} }},
                    y: {{ ticks: {{ stepSize: 1, font: {{ size: 10 }}, color: '#101828' }}, grid: {{ color: '#F2F4F7' }}, beginAtZero: true }}
                }}
            }}
        }});
        </script>""", height=340, scrolling=False)

with col_traffic:
    traffic_data = {
        "Jan": [["Northeastern",4821],["Google",3102],["Social Media",1850]],
        "Feb": [["Google",5200],["Northeastern",3800],["Social Media",2100]],
        "Mar": [["Google",6100],["Northeastern",4200],["Social Media",2800]],
        "Apr": [["Google",7300],["Northeastern",4900],["Social Media",3200]],
    }
    month_opts = "".join(f'<option value="{m}"{"selected" if m=="Apr" else ""}>{m}</option>' for m in traffic_data)
    components.html(f"""
    <div style="background:white;border:1px solid #EAECF0;border-radius:12px;padding:1.25rem;box-shadow:0 1px 2px rgba(16,24,40,0.04);font-family:'Source Sans Pro',sans-serif;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.25rem;">
            <div style="font-size:1.1rem;font-weight:700;color:#101828;">Traffic Sources</div>
            <select id="ms" style="border:1px solid #EAECF0;border-radius:6px;padding:4px 10px;font-size:0.85rem;color:#101828;">{month_opts}</select>
        </div>
        <div id="tb"></div>
    </div>
    <script>
    const d = {json.dumps(traffic_data)};
    const clr = {{"Northeastern":"#6366f1","Google":"#8b5cf6","Social Media":"#22c55e"}};
    function render(m) {{
        const rows = d[m];
        const mx = Math.max(...rows.map(r=>r[1]));
        document.getElementById('tb').innerHTML = rows.map(([lbl,val]) =>
            `<div style="margin-bottom:1.1rem;">
                <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                    <span style="font-size:0.92rem;font-weight:600;color:#101828;">${{lbl}}</span>
                    <span style="font-size:0.92rem;color:#667085;">${{val.toLocaleString()}}</span>
                </div>
                <div style="background:#F2F4F7;border-radius:4px;height:10px;">
                    <div style="background:${{clr[lbl]||'#E31B1B'}};border-radius:4px;height:10px;width:${{Math.round(val/mx*100)}}%;"></div>
                </div>
            </div>`
        ).join('');
    }}
    render('Apr');
    document.getElementById('ms').addEventListener('change',e=>render(e.target.value));
    </script>""", height=280, scrolling=False)
