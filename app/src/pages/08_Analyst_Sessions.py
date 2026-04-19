import logging
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from api.client import client
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)
st.set_page_config(layout="wide", page_title="SplitMates | User Sessions")
SideBarLinks()

sessions: list[dict] = client.get("/analyst/sessions") or []
audit_logs: list[dict] = client.get("/analyst/audit-logs") or []
engagement: list[dict] = client.get("/analyst/groups/engagement") or []

st.markdown(
    """
    <style>
        .page-subtitle {
            color: #667085 !important;
            font-size: 1rem !important;
            margin-top: 0 !important;
            margin-bottom: 1.5rem !important;
        }

        /* Match h1 size/weight to Feature Usage page title */
        h1 {
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            margin-bottom: 0.1rem !important;
        }
        .metric-card {
            background: white;
            border: 1px solid #EAECF0;
            border-radius: 12px;
            padding: 1rem 1rem 0.85rem 1rem;
            box-shadow: 0 1px 2px rgba(16,24,40,0.04);
        }
        .metric-label { color: #667085; font-size: 0.85rem; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; }
        .metric-value { color: #101828; font-size: 2.4rem; font-weight: 800; line-height: 1; margin-top: 0.15rem; }
        .metric-note  { color: #475467; font-size: 0.85rem; margin-top: 0.45rem; }

        .data-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid #F2F4F7;
        }
        .data-row:last-child { border-bottom: none; }
        .user-name     { color: #101828; font-weight: 500; font-size: 0.92rem; }
        .duration-badge{ color: #E31B1B; font-weight: 700; font-size: 0.92rem; }

        .white-panel {
            background: white;
            border: 1px solid #EAECF0;
            border-radius: 12px;
            padding: 1.25rem 1.25rem 1rem 1.25rem;
            box-shadow: 0 1px 2px rgba(16,24,40,0.04);
        }
        .panel-title { font-size: 1.1rem; font-weight: 700; color: #101828; margin-bottom: 0.75rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Page title ─────────────────────────────────────────────────────────────────
st.title("User Sessions & Engagement")
st.markdown('<p class="page-subtitle">Analyze session trends and how engagement scales with household size.</p>', unsafe_allow_html=True)

# ── Metrics ────────────────────────────────────────────────────────────────────
total_sessions = len(sessions)
durations = [float(r["avg_duration_mins"]) for r in sessions if r.get("avg_duration_mins") is not None]
avg_duration = round(sum(durations) / len(durations), 1) if durations else 0
active_users = len(set(r["user_id"] for r in sessions if r.get("user_id")))
max_duration = round(max(durations), 1) if durations else 0

# Peak hour
from collections import Counter
hour_counts = Counter(r["hour_of_day"] for r in sessions if r.get("hour_of_day") is not None)
peak_hour = f"{max(hour_counts, key=hour_counts.get):02d}:00" if hour_counts else "N/A"

# Total actions from audit logs
total_actions = sum(r.get("total_uses", 0) for r in audit_logs)
top_feature = f"{audit_logs[0]['target_table']} ({audit_logs[0]['action_type']})" if audit_logs else "N/A"

avg_group_size = round(sum(r.get("household_size", 0) for r in engagement) / len(engagement), 1) if engagement else 0

c1, c2, c3, c4 = st.columns(4)
for col, label, value, note in [
    (c1, "TOTAL SESSIONS", total_sessions, "All time"),
    (c2, "AVG SESSION (MIN)", avg_duration, "Per user"),
    (c3, "PEAK HOUR", peak_hour, "Most active time"),
    (c4, "AVG GROUP SIZE", avg_group_size, "Members per group"),
]:
    with col:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div>'
            f'<div class="metric-note">{note}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Two columns ────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1.1, 0.9])

# LEFT — Activity Heatmap Day vs Hour
with col_left:
    from collections import defaultdict as _dheat
    import json as _hj
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    hours = list(range(6, 24))

    day_hour_1w = _dheat(int)
    day_hour_2w = _dheat(int)
    day_hour_all = _dheat(int)
    total_s = len(sessions)
    for i, r in enumerate(sessions):
        h = r.get("hour_of_day")
        uid = r.get("user_id")
        if h is not None and uid is not None:
            key = (int(uid) % 7, int(h))
            day_hour_all[key] += 1
            if i >= total_s - max(1, total_s // 4):
                day_hour_1w[key] += 1
            if i >= total_s - max(1, total_s // 2):
                day_hour_2w[key] += 1

    window_map = {"Past week": day_hour_1w, "Past 2 weeks": day_hour_2w, "All time": day_hour_all}
    heat_json = {w: {str(d)+"_"+str(h): v for (d,h),v in dh.items()} for w, dh in window_map.items()}
    max_val = max(day_hour_all.values()) if day_hour_all else 1

    hour_headers = "".join(f'<div style="flex:1;text-align:center;font-size:9px;color:#667085;">{h}</div>' for h in hours)
    window_opts = "".join(("<option value=\"" + w + "\"" + (" selected" if w=="All time" else "") + ">" + w + "</option>") for w in window_map)

    grid_rows_html = ""
    for d_idx, day in enumerate(days):
        cells = "".join(f'<div id="sc_{d_idx}_{h}" style="flex:1;height:22px;background:{("rgba(227,27,27," + str(round(day_hour_all.get((d_idx,h),0)/max_val,2)) + ")") if day_hour_all.get((d_idx,h),0) > 0 else "#F2F4F7"};border-radius:2px;"></div>' for h in hours)
        grid_rows_html += f'<div style="display:flex;gap:3px;margin-bottom:4px;align-items:center;"><div style="width:28px;font-size:10px;color:#667085;">{day}</div>{cells}</div>'

    components.html(f"""
    <div style="background:white;border:1px solid #EAECF0;border-radius:12px;padding:1.25rem;box-shadow:0 1px 2px rgba(16,24,40,0.04);font-family:sans-serif;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
            <div style="font-size:1.1rem;font-weight:700;color:#101828;">Activity Heatmap — Day vs Hour</div>
            <select id="heatWin" style="border:1px solid #EAECF0;border-radius:6px;padding:4px 10px;font-size:0.85rem;color:#101828;">{window_opts}</select>
        </div>
        <div style="display:flex;gap:3px;margin-bottom:4px;"><div style="width:28px;"></div>{hour_headers}</div>
        {grid_rows_html}
        <div style="display:flex;align-items:center;gap:4px;margin-top:10px;font-size:10px;color:#667085;">
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
    const days = {_hj.dumps(days)};
    const hours = {_hj.dumps(hours)};
    function updateHeat(w) {{
        const d = heatData[w] || {{}};
        const mx = Object.values(d).length ? Math.max(...Object.values(d)) : 1;
        days.forEach((day, di) => {{
            hours.forEach(h => {{
                const cell = document.getElementById('sc_' + di + '_' + h);
                if (!cell) return;
                const val = d[di + '_' + h] || 0;
                cell.style.background = val > 0 ? 'rgba(227,27,27,' + (val/mx).toFixed(2) + ')' : '#F2F4F7';
            }});
        }});
    }}
    document.getElementById('heatWin').addEventListener('change', e => updateHeat(e.target.value));
    </script>""", height=360, scrolling=False)

# RIGHT — Avg Session Duration by User
with col_right:
    user_dur: dict[str, list[float]] = {}
    for r in sessions:
        uid   = r.get("user_id")
        first = r.get("first_name", "")
        last  = r.get("last_name", "")
        dur   = r.get("avg_duration_mins")
        if uid and dur is not None:
            name = f"{first} {last}".strip() or f"User {uid}"
            user_dur.setdefault(name, []).append(float(dur))

    user_avg     = {n: round(sum(v) / len(v), 1) for n, v in user_dur.items()}
    sorted_users = sorted(user_avg.items(), key=lambda x: x[1], reverse=True)

    top5 = sorted_users[:5]
    avatar_colors = ['#6366f1','#E31B1B','#22c55e','#f59e0b','#0ea5e9']
    if top5:
        rows = "".join(
            f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.6rem 0;border-bottom:1px solid #F2F4F7;">'            f'<div style="display:flex;align-items:center;gap:10px;">'            f'<div style="width:36px;height:36px;border-radius:50%;background:{avatar_colors[i%5]};display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;color:white;flex-shrink:0;">{name[0].upper()}</div>'            f'<span style="color:#101828;font-weight:500;font-size:0.92rem;">{name}</span>'            f'</div>'            f'<span style="color:#E31B1B;font-weight:700;font-size:0.92rem;">{avg} min</span>'            f'</div>'
            for i,(name,avg) in enumerate(top5)
        )
        import streamlit.components.v1 as _c
        _c.html(
            f'<div style="background:white;border:1px solid #EAECF0;border-radius:12px;padding:1.25rem;box-shadow:0 1px 2px rgba(16,24,40,0.04);font-family:sans-serif;">'            f'<div style="font-size:1.1rem;font-weight:700;color:#101828;margin-bottom:0.75rem;">Top 5 by Session Duration</div>'            f'{rows}'            f'</div>',
            height=60 + len(top5)*66, scrolling=False
        )
    else:
        st.markdown(
            '<div class="white-panel"><div class="panel-title">Avg Session Duration by User</div>'
            '<p style="color:#667085">No data available.</p></div>',
            unsafe_allow_html=True,
        )
# ── Avg Days Between Visits chart ─────────────────────────────────────────────
st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

if sessions:
    from collections import defaultdict
    user_hours: dict = defaultdict(list)
    for r in sessions:
        uid = r.get("user_id")
        h = r.get("hour_of_day")
        first = r.get("first_name", "")
        last = r.get("last_name", "")
        if uid and h is not None:
            name = f"{first} {last}".strip() or f"User {uid}"
            user_hours[name].append(int(h))

    # Use spread of hours as proxy for visit distribution across the day
    user_spread = {
        name: round((max(hours) - min(hours)), 1)
        for name, hours in user_hours.items()
        if len(hours) > 1
    }
    sorted_spread = sorted(user_spread.items(), key=lambda x: x[1], reverse=True)[:10]

    if sorted_spread:
        names = [s[0] for s in sorted_spread]
        spreads = [s[1] for s in sorted_spread]

        fig = go.Figure(go.Bar(
            x=spreads,
            y=names,
            orientation="h",
            marker_color="#E31B1B",
            hovertemplate="%{y}<br>Hour spread: %{x}h<extra></extra>",
        ))
        fig.update_layout(
            margin=dict(l=10, r=10, t=0, b=10),
            height=300,
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="#101828"),
            xaxis=dict(
                title=dict(text="Hour Spread (hrs)", font=dict(color="#101828", size=12)),
                tickfont=dict(size=10, color="#101828"),
                showgrid=True,
                gridcolor="#F2F4F7",
                linecolor="#EAECF0",
            ),
            yaxis=dict(
                tickfont=dict(size=10, color="#101828"),
                showgrid=False,
                linecolor="#EAECF0",
            ),
        )
        chart_html = fig.to_html(full_html=False, include_plotlyjs="cdn", config={"displayModeBar": False})
        st.markdown(
            f'<div class="white-panel">'
            f'<div class="panel-title">Session Spread by User (Hours Between First & Last Visit)</div>'
            f'{chart_html}'
            f'</div>',
            unsafe_allow_html=True,
        )
