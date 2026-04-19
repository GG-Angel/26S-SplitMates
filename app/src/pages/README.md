# `pages` Folder

This folder contains all the pages that will be part of the application. Pages are automatically discovered and ordered by Streamlit based on their numeric prefix.

## Page Organization

Pages are organized by role/persona with numeric prefixes that control sidebar ordering:

### Roommate Pages (00-07)
- **00_User_Dashboard.py** - Roommate home; view and select groups
- **01_Group_Creation.py** - Create a new roommate group
- **02_Group_Dashboard.py** - Group dashboard; overview and stats
- **03_Group_Events.py** - Event management for the current group
- **04_Create_Event.py** - Create a new group event
- **05_Group_Bills.py** - Bill tracking and splitting
- **06_Group_Chores.py** - Chore assignment and tracking
- **07_Group_Management.py** - Group admin tools for group leaders

### Analyst Pages (07-09)
- **07_Analyst_Feature_Usage.py** - Feature usage analytics
- **08_Analyst_Sessions.py** - Session analytics
- **09_Analyst_Inactive_Users.py** - Inactive user reporting

### System Admin Pages (20-25)
- **20_Admin_Home.py** - Admin dashboard with KPIs
- **21_Admin_Tickets.py** - Support ticket management
- **22_Admin_User_Reports.py** - User report management
- **23_Admin_Groups.py** - Group management
- **24_Admin_Roommates.py** - User/roommate management
- **25_Admin_Ops_And_Logs.py** - Audit logs and operations

### Other Pages
- **30_About.py** - About page

## Authentication & Navigation

Page access is controlled by role in `modules/nav.py`. The sidebar is built dynamically based on the logged-in user's role:
- **roommate**: Group selection, group workflows
- **analyst**: Feature usage, sessions, and inactive-user pages
- **administrator**: System admin panel with full management access

See `modules/nav.py` for navigation logic and `Home.py` for authentication flow.
