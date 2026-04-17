import logging
from typing import Any

import streamlit as st

from modules.admin_api import delete_admin_group, get_admin_group, get_admin_groups
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide", page_title="SplitMates | Admin Groups")
SideBarLinks()


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _card(label: str, value: Any, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <style>
        .page-title { font-size: 2.1rem; font-weight: 800; margin-bottom: 0.1rem; }
        .page-subtitle { color: #667085; font-size: 1rem; margin-bottom: 1rem; }
        .metric-card {
            background: #F8FAFC;
            border: 1px solid #EAECF0;
            border-radius: 12px;
            padding: 1rem 1rem 0.85rem 1rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
            height: 100%;
        }
        .metric-label { color: #667085; font-size: 0.83rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
        .metric-value { color: #101828; font-size: 2.4rem; font-weight: 800; line-height: 1; margin-top: 0.15rem; }
        .metric-note { color: #475467; font-size: 0.85rem; margin-top: 0.45rem; }
        .panel {
            background: #F8FAFC;
            border: 1px solid #EAECF0;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        }
        .panel-title { font-size: 1.12rem; font-weight: 700; margin-bottom: 0.35rem; color: #101828; }
        .row {
            padding: 0.8rem 0;
            border-bottom: 1px solid #EAECF0;
        }
        .row:last-child { border-bottom: none; }
        .row-title { font-weight: 700; color: #101828; font-size: 0.98rem; }
        .row-meta { color: #667085; font-size: 0.85rem; margin-top: 0.18rem; }
        .pill {
            display: inline-block;
            padding: 0.2rem 0.55rem;
            border-radius: 8px;
            font-size: 0.76rem;
            font-weight: 700;
            margin-top: 0.3rem;
            margin-right: 0.35rem;
            background: #ECFDF3;
            color: #027A48;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="page-title">Roommate Groups</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Monitor household groups, inspect membership, and remove inactive groups safely.</div>',
    unsafe_allow_html=True,
)

try:
    groups = get_admin_groups() or []
except Exception as exc:
    st.error(f"Unable to load groups: {exc}")
    st.stop()

total_members = sum(int(g.get("member_count") or 0) for g in groups)
leader_set = {_as_text(g.get("group_leader")) for g in groups if g.get("group_leader") is not None}
avg_group_size = round((total_members / len(groups)), 1) if groups else 0

k1, k2, k3, k4 = st.columns(4)
with k1:
    _card("Total Groups", len(groups), "Current households")
with k2:
    _card("Total Members", total_members, "Across all groups")
with k3:
    _card("Avg Group Size", avg_group_size, "Members per group")
with k4:
    _card("Group Leaders", len(leader_set), "Unique leaders")

left_col, right_col = st.columns([0.36, 0.64], gap="large")

filtered_groups: list[dict[str, Any]] = groups
selected_group_id = None

with left_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Filters</div>', unsafe_allow_html=True)
    search_term = st.text_input("Search groups", placeholder="Search by group name, id, or leader id")
    min_members = st.number_input("Minimum members", min_value=0, value=0)

    if search_term:
        needle = search_term.lower()
        filtered_groups = [
            group
            for group in filtered_groups
            if needle in _as_text(group.get("name")).lower()
            or needle in _as_text(group.get("group_id")).lower()
            or needle in _as_text(group.get("group_leader")).lower()
        ]

    filtered_groups = [
        group for group in filtered_groups if int(group.get("member_count") or 0) >= int(min_members)
    ]

    st.caption(f"Showing {len(filtered_groups)} of {len(groups)} groups")

    if filtered_groups:
        selected_group_id = st.selectbox(
            "Select group",
            [group["group_id"] for group in filtered_groups],
            format_func=lambda group_id: f"#{group_id} — {next((_as_text(g.get('name')) or 'Unnamed Group') for g in filtered_groups if g.get('group_id') == group_id)}",
        )
        st.divider()
        st.markdown('<div class="panel-title">Filtered List</div>', unsafe_allow_html=True)
        for group in filtered_groups[:8]:
            st.markdown(
                f"""
                <div class="row">
                    <div class="row-title">{_as_text(group.get('name')) or 'Unnamed Group'}</div>
                    <div class="row-meta">Group #{group.get('group_id')} • Leader #{group.get('group_leader')}</div>
                    <span class="pill">{group.get('member_count', 0)} members</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No groups match the selected filters.")

    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Group Details</div>', unsafe_allow_html=True)

    if selected_group_id is None:
        st.caption("Choose a group from the left panel to review details.")
    else:
        try:
            detail = get_admin_group(selected_group_id)
        except Exception as exc:
            st.error(f"Unable to load group details: {exc}")
            st.stop()

        st.markdown(
            f"""
            <div class="row" style="padding-top:0;">
                <div class="row-title">{_as_text(detail.get('name')) or 'Unnamed Group'}</div>
                <div class="row-meta">Group #{detail.get('group_id')} • Leader #{detail.get('group_leader')}</div>
                <div class="row-meta">Address: {_as_text(detail.get('address')) or 'N/A'}, {_as_text(detail.get('city')) or ''} {_as_text(detail.get('state')) or ''} {_as_text(detail.get('zip_code')) or ''}</div>
                <span class="pill">{detail.get('member_count', 0)} members</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Delete group", type="primary", use_container_width=True):
            try:
                delete_admin_group(selected_group_id)
                st.success("Group deleted.")
                st.rerun()
            except Exception as exc:
                st.error(f"Unable to delete group: {exc}")

    st.markdown("</div>", unsafe_allow_html=True)
