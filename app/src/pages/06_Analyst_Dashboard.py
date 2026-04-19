import logging
import json
import streamlit as st
import streamlit.components.v1 as components
from api.client import client
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide", page_title="SplitMates | Dashboard Overview")
SideBarLinks()

audit_activity: list[dict] = client.get("/analyst/audit-logs/activity") or []
sessions: list[dict] = client.get("/analyst/sessions") or []
inactive_users: list[dict] = client.get("/analyst/users/inactive") or []
audit_logs: list[dict] = client.get("/analyst/audit-logs") or []

st.markdown("""
<style>
    h1 { font-size: 2.2rem !important; font-weight: 700 !important; margin-bottom: 0.1rem !important; }
    .page-subtitle { color: #667085; font-size: 1rem; margin-top: 0; margin-bottom: 1.5rem; }
    .metric-card { background: white; border: 1px solid #EAECF0; border-radius: 12px;
        padding: 1rem 1rem 0.85rem 1rem; box-shadow: 0 1px 2px rgba(16,24,40,0.04); height: 100%; }
    .metric-label { color: #667085; font-size: 0.85rem; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; }
    .metric-value { color: #101828; font-size: 2.4rem; font-weight: 800; line-height: 1; margin-top: 0.15rem; }
    .metric-note { color: #475467; font-size: 0.85rem; margin-top: 0.45rem; }
</style>""", unsafe_allow_html=True)

st.title("Dashboard Overview")
st.markdown('<div class="page-subtitle">High-level platform health and engagement at a glance.</div>', unsafe_allow_html=True)

total_sessions = len(sessions)
active_users = len(set(r.get("user_id") for r in sessions if r.get("user_id")))
inactive_count = len(inactive_users)
total_actions = sum(r.get("total_uses", 0) for r in audit_logs)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">TOTAL SESSIONS</div><div class="metric-value">{total_sessions}</div><div class="metric-note">All time</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><div class="metric-label">ACTIVE USERS</div><div class="metric-value">{active_users}</div><div class="metric-note">With sessions</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><div class="metric-label">INACTIVE USERS</div><div class="metric-value">{inactive_count}</div><div class="metric-note">14+ days</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card"><div class="metric-label">TOTAL ACTIONS</div><div class="metric-value">{total_actions}</div><div class="metric-note">Platform wide</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_line, col_traffic = st.columns(2, gap="large")

with col_line:
    if audit_activity:
        dates = [r["date"][:16] for r in audit_activity]
        acts = [r["actions"] for r in audit_activity]
        components.html(f"""
        <div style="background:white;border:1px solid #EAECF0;border-radius:12px;
                    padding:1.25rem;box-shadow:0 1px 2px rgba(16,24,40,0.04);">
            <div style="font-size:1.1rem;font-weight:700;color:#101828;margin-bottom:1rem;
                        font-family:sans-serif;">Platform Activity Over Time</div>
            <div style="position:relative;height:280px;">
                <canvas id="lineChart" role="img" aria-label="Platform activity over time">Activity trend Jan-Apr 2026</canvas>
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
        </script>""", height=380, scrolling=False)

with col_traffic:
    traffic_data = {
        "Jan": [["Northeastern",4821],["Google",3102],["Social Media",1850]],
        "Feb": [["Google",5200],["Northeastern",3800],["Social Media",2100]],
        "Mar": [["Google",6100],["Northeastern",4200],["Social Media",2800]],
        "Apr": [["Google",7300],["Northeastern",4900],["Social Media",3200]],
    }
    month_opts = "".join(f'<option value="{m}"{"selected" if m=="Apr" else ""}>{m}</option>' for m in traffic_data)
    components.html(f"""
    <div style="background:white;border:1px solid #EAECF0;border-radius:12px;
                padding:1.25rem;box-shadow:0 1px 2px rgba(16,24,40,0.04);font-family:sans-serif;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.25rem;">
            <div style="font-size:1.1rem;font-weight:700;color:#101828;">Traffic Sources</div>
            <select id="ms" style="border:1px solid #EAECF0;border-radius:6px;padding:4px 10px;
                    font-size:0.85rem;color:#101828;">{month_opts}</select>
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
            `<div style="margin-bottom:1.2rem;">
                <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                    <span style="font-size:0.92rem;font-weight:600;color:#101828;">${{lbl}}</span>
                    <span style="font-size:0.92rem;color:#667085;">${{val.toLocaleString()}}</span>
                </div>
                <div style="background:#F2F4F7;border-radius:4px;height:12px;">
                    <div style="background:${{clr[lbl]||'#E31B1B'}};border-radius:4px;height:12px;width:${{Math.round(val/mx*100)}}%;"></div>
                </div>
            </div>`
        ).join('');
    }}
    render('Apr');
    document.getElementById('ms').addEventListener('change',e=>render(e.target.value));
    </script>""", height=320, scrolling=False)
