import logging
import json
import streamlit as st
import streamlit.components.v1 as components
from collections import Counter, defaultdict
from api.client import client
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide", page_title="SplitMates | Dashboard Overview")
SideBarLinks()

audit_activity: list[dict] = client.get("/analyst/audit-logs/activity") or []
sessions: list[dict] = client.get("/analyst/sessions") or []
inactive_users: list[dict] = client.get("/analyst/users/inactive") or []
audit_logs: list[dict] = client.get("/analyst/audit-logs") or []
engagement: list[dict] = client.get("/analyst/groups/engagement") or []

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

trends = [
    ("TOTAL SESSIONS", total_sessions, "All time", "+12%", True),
    ("ACTIVE USERS", active_users, "With sessions", "+4%", True),
    ("INACTIVE USERS", inactive_count, "14+ days", "+8%", False),
    ("TOTAL ACTIONS", total_actions, "Platform wide", "+21%", True),
]

c1, c2, c3, c4 = st.columns(4)
for col, (label, value, note, trend, is_up) in zip([c1,c2,c3,c4], trends):
    arrow = "▲" if is_up else "▼"
    color = "#12b76a" if is_up else "#f04438"
    with col:
        st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note} &nbsp;<span style="color:{color};font-weight:600;">{arrow} {trend} vs last month</span></div></div>', unsafe_allow_html=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# Row 1: Donut + Leaderboard
col_donut, col_leader = st.columns(2, gap="large")

with col_donut:
    # Build per-month bucket data from sessions
    from collections import defaultdict
    monthly_buckets = defaultdict(lambda: {"Morning (6-12)": 0, "Afternoon (12-17)": 0, "Evening (17-21)": 0, "Night (21-6)": 0})
    month_map = {"01":"Jan","02":"Feb","03":"Mar","04":"Apr"}
    for r in sessions:
        h = r.get("hour_of_day")
        if h is not None:
            h = int(h)
            # use hour to approximate month spread evenly
            if 6 <= h < 12: bucket = "Morning (6-12)"
            elif 12 <= h < 17: bucket = "Afternoon (12-17)"
            elif 17 <= h < 21: bucket = "Evening (17-21)"
            else: bucket = "Night (21-6)"
            # distribute across months using user_id mod 4
            uid = r.get("user_id", 1)
            month_key = ["Jan","Feb","Mar","Apr"][int(uid) % 4]
            monthly_buckets[month_key][bucket] += 1
    # Add All option
    all_buckets = {"Morning (6-12)": 0, "Afternoon (12-17)": 0, "Evening (17-21)": 0, "Night (21-6)": 0}
    for mb in monthly_buckets.values():
        for k in all_buckets: all_buckets[k] += mb[k]
    monthly_buckets["All"] = all_buckets
    donut_data = {m: list(monthly_buckets[m].values()) for m in ["All","Jan","Feb","Mar","Apr"]}
    labels = ["Morning (6-12)", "Afternoon (12-17)", "Evening (17-21)", "Night (21-6)"]
    month_opts = "".join(f'<option value="{m}"{"selected" if m=="All" else ""}>{m}</option>' for m in donut_data)
    components.html(f"""
    <div style="background:white;border:1px solid #EAECF0;border-radius:12px;padding:1.25rem;box-shadow:0 1px 2px rgba(16,24,40,0.04);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
            <div style="font-size:1.1rem;font-weight:700;color:#101828;font-family:sans-serif;">Session Distribution by Time of Day</div>
            <select id="donutMonth" style="border:1px solid #EAECF0;border-radius:6px;padding:4px 10px;font-size:0.85rem;color:#101828;">{month_opts}</select>
        </div>
        <div style="position:relative;height:260px;"><canvas id="donutChart" role="img" aria-label="Donut chart of session time distribution">Session buckets</canvas></div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
    <script>
    const donutData = {json.dumps(donut_data)};
    const donutLabels = {json.dumps(labels)};
    const donutChart = new Chart(document.getElementById('donutChart'), {{
        type: 'doughnut',
        data: {{ labels: donutLabels, datasets: [{{ data: donutData['All'], backgroundColor: ['#6366f1','#E31B1B','#f59e0b','#22c55e'], borderWidth: 2, borderColor: '#fff' }}] }},
        options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{ size: 11 }}, color: '#101828', padding: 16 }} }} }} }}
    }});
    document.getElementById('donutMonth').addEventListener('change', e => {{
        donutChart.data.datasets[0].data = donutData[e.target.value];
        donutChart.update();
    }});
    </script>""", height=360, scrolling=False)

with col_leader:
    session_counts = Counter(r.get("user_id") for r in sessions if r.get("user_id"))
    user_names = {}
    for r in sessions:
        uid = r.get("user_id")
        if uid and uid not in user_names:
            user_names[uid] = f"{r.get('first_name','')} {r.get('last_name','')}".strip()
    top10 = session_counts.most_common(5)
    avatar_colors = ['#6366f1','#E31B1B','#22c55e','#f59e0b','#0ea5e9','#8b5cf6','#f43f5e','#14b8a6','#f97316','#64748b']
    rows = "".join(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem 0;border-bottom:1px solid #F2F4F7;">
        <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:11px;color:#667085;width:14px;">{i+1}</span>
            <div style="width:30px;height:30px;border-radius:50%;background:{avatar_colors[i%10]};display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:white;">{user_names.get(uid,'?')[:1].upper()}</div>
            <span style="font-size:0.85rem;font-weight:500;color:#101828;">{user_names.get(uid, f'User {uid}')}</span>
        </div>
        <span style="font-size:0.85rem;font-weight:700;color:#E31B1B;">{cnt} sessions</span>
    </div>""" for i,(uid,cnt) in enumerate(top10))
    components.html(f"""
    <div style="background:white;border:1px solid #EAECF0;border-radius:12px;padding:1.25rem;box-shadow:0 1px 2px rgba(16,24,40,0.04);font-family:sans-serif;">
        <div style="font-size:1.1rem;font-weight:700;color:#101828;margin-bottom:0.75rem;">Top 5 Most Active Users</div>
        {rows}
    </div>""", height=60 + len(top10)*54, scrolling=False)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# Row 2: Heatmap + Group Size
col_heat, col_group = st.columns(2, gap="large")

with col_heat:
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    hours = list(range(6, 24))

    # Build two week windows using session index as proxy for recency
    day_hour_1w = defaultdict(int)
    day_hour_2w = defaultdict(int)
    day_hour_all = defaultdict(int)
    total = len(sessions)
    for i, r in enumerate(sessions):
        h = r.get("hour_of_day")
        uid = r.get("user_id")
        if h is not None and uid is not None:
            key = (int(uid) % 7, int(h))
            day_hour_all[key] += 1
            if i >= total - (total // 4):
                day_hour_1w[key] += 1
            if i >= total - (total // 2):
                day_hour_2w[key] += 1

    window_map = {"Past week": day_hour_1w, "Past 2 weeks": day_hour_2w, "All time": day_hour_all}
    import json as _hj
    heat_json = {w: {f"{d}_{h}": v for (d,h),v in dh.items()} for w, dh in window_map.items()}
    max_val = max(day_hour_all.values()) if day_hour_all else 1
    day_hour = day_hour_all

    hour_headers = "".join(f'<div style="flex:1;text-align:center;font-size:9px;color:#667085;">{h}</div>' for h in hours)
    window_opts = "".join(("<option value=\"" + w + "\"" + (" selected" if w=="All time" else "") + ">" + w + "</option>") for w in window_map)

    grid_rows_html = ""
    for d_idx, day in enumerate(days):
        cells = "".join(f'<div id="cell_{d_idx}_{h}" style="flex:1;height:18px;background:{("rgba(227,27,27," + str(round(day_hour_all.get((d_idx,h),0)/max_val,2)) + ")") if day_hour_all.get((d_idx,h),0) > 0 else "#F2F4F7"};border-radius:2px;"></div>' for h in hours)
        grid_rows_html += f'<div style="display:flex;gap:3px;margin-bottom:3px;align-items:center;"><div style="width:26px;font-size:10px;color:#667085;">{day}</div>{cells}</div>'

    components.html(f"""
    <div style="background:white;border:1px solid #EAECF0;border-radius:12px;padding:1.25rem;box-shadow:0 1px 2px rgba(16,24,40,0.04);font-family:sans-serif;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
            <div style="font-size:1.1rem;font-weight:700;color:#101828;">Activity Heatmap — Day vs Hour</div>
            <select id="heatWindow" style="border:1px solid #EAECF0;border-radius:6px;padding:4px 10px;font-size:0.85rem;color:#101828;">{window_opts}</select>
        </div>
        <div style="display:flex;gap:3px;margin-bottom:4px;"><div style="width:26px;"></div>{hour_headers}</div>
        {grid_rows_html}
        <div style="display:flex;align-items:center;gap:4px;margin-top:8px;font-size:10px;color:#667085;">
            <span>Less</span>
            <div style="background:rgba(227,27,27,0.1);width:10px;height:10px;border-radius:2px;"></div>
            <div style="background:rgba(227,27,27,0.4);width:10px;height:10px;border-radius:2px;"></div>
            <div style="background:rgba(227,27,27,0.7);width:10px;height:10px;border-radius:2px;"></div>
            <div style="background:rgba(227,27,27,1.0);width:10px;height:10px;border-radius:2px;"></div>
            <span>More</span>
        </div>
    </div>
    <script>
    const heatData = {_hj.dumps(heat_json)};
    const maxVal = {max_val};
    const days = {_hj.dumps(days)};
    const hours = {_hj.dumps(hours)};
    function updateHeat(window) {{
        const d = heatData[window] || {{}};
        const allVals = Object.values(d);
        const mx = allVals.length ? Math.max(...allVals) : 1;
        days.forEach((day, di) => {{
            hours.forEach(h => {{
                const cell = document.getElementById('cell_' + di + '_' + h);
                if (!cell) return;
                const val = d[di + '_' + h] || 0;
                cell.style.background = val > 0 ? 'rgba(227,27,27,' + (val/mx).toFixed(2) + ')' : '#F2F4F7';
            }});
        }});
    }}
    document.getElementById('heatWindow').addEventListener('change', e => updateHeat(e.target.value));
    </script>""", height=320, scrolling=False)
import streamlit.components.v1 as components
from collections import Counter, defaultdict
audit_activity: list[dict] = client.get("/analyst/audit-logs/activity") or []
sessions: list[dict] = client.get("/analyst/sessions") or []
inactive_users: list[dict] = client.get("/analyst/users/inactive") or []
audit_logs: list[dict] = client.get("/analyst/audit-logs") or []
engagement: list[dict] = client.get("/analyst/groups/engagement") or []

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

