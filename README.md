# SplitMates

SplitMates is a roommate management app for CS 3200 (Spring 2026). It helps roommates track shared bills, chores, and group events, and provides a system administrator interface for managing users, support tickets, and app operations.

## Prerequisites

- A GitHub Account
- A terminal-based git client or GUI Git client such as GitHub Desktop or the Git plugin for VSCode.
- A distribution of Python running on your laptop. The distribution supported by the course is [Anaconda](https://www.anaconda.com/download) or [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install).
  - Create a new Python 3.11 environment in `conda` named `db-proj` by running:  
     ```bash
     conda create -n db-proj python=3.11
     ```
  - Install the Python dependencies listed in `api/requirements.txt` and `app/src/requirements.txt` into your local Python environment. You can do this by running `pip install -r requirements.txt` in each respective directory.
     ```bash
     cd api
     pip install -r requirements.txt
     cd ../app/src
     pip install -r requirements.txt
     ```
     Note that the `..` means go to the parent folder of the folder you're currently in (which is `api/` after the first command).
     > **Why install locally if everything runs in Docker?** Installing the packages locally lets your IDE (VSCode) provide autocompletion, linting, and error highlighting as you write code. The app itself always runs inside the Docker containers — the local install is just for editor support.
- VSCode with the Python Plugin installed
  - You may use some other Python/code editor.  However, Course staff will only support VS Code. 


## Structure of the Repo

- This repository is organized into the main project folders:
   - `./app` - the Streamlit app
   - `./api` - the Flask REST API
   - `./database-files` - SQL scripts to initialize the MySQL database
   - `./seeder` - Python seed script for mock data
   - `./docs` - project documentation

- The repo also contains a `docker-compose.yaml` file that is used to set up the Docker containers for the front end app, the REST API, MySQL database, and the seeder.

## Suggestion for Learning the Project Code Base

If you are not familiar with web app development, this code base might be confusing. But don't worry, we'll get through it together. Here are some suggestions for learning the code base:

1. Start by exploring the `./app` directory. This is where the Streamlit app is located. The Streamlit app is a Python-based web app that is used to interact with the user. It's a great way to build a simple web app without having to learn a lot of web development.
1. Next, explore the `./api` directory. This is where the Flask REST API is located. The REST API is used to interact with the database and perform other server-side tasks. You might also consider this the "application logic" or "business logic" layer of your app. 
1. Finally, explore the `./database-files` directory. This is where the SQL scripts are located that will be used to initialize the MySQL database.
1. Bonus: If you want to have a totally separate copy of the Template Repo on your laptop that you can use to explore and try things without messing up your team repo, see *Setting Up a Personal Testing Repo (Optional)* section below. 

## Setting Up the Repos
<details>
<summary>Setting Up a Personal Sandbox Repo (Optional)</summary>

### Setting Up a Personal Sandbox Repo (Optional)

**Before you start**: You need to have a GitHub account and a terminal-based git client or GUI Git client such as GitHub Desktop or the Git plugin for VSCode.

1. Clone this repo to your local machine.
   1. You can do this by clicking the green "Code" button on the top right of the repo page and copying the URL. Then, in your terminal, run `git clone <URL>`.
   1. Or, you can use the GitHub Desktop app to clone the repo. See [this page](https://docs.github.com/en/desktop/adding-and-cloning-repositories/cloning-a-repository-from-github-to-github-desktop) of the GitHub Desktop Docs for more info. 
1. Open the repository folder in VSCode.
1. Set up the `.env` file in the `api` folder based on the `.env.template` file.
   1. Make a copy of the `.env.template` file and name it `.env`. 
   1. Open the new `.env` file. 
   1. On the last line, delete the `<...>` placeholder text, and put a password. Don't reuse any passwords you use for any other services (email, etc.) 
1. For running the testing containers (for your personal repo), you will tell `docker compose` to use a different configuration file than the typical one.  The one you will use for testing is `sandbox.yaml`.
   1. `docker compose -f sandbox.yaml up -d` to start all the containers in the background
   1. `docker compose -f sandbox.yaml down` to shutdown and delete the containers
   1. `docker compose -f sandbox.yaml up db -d` only start the database container (replace db with api or app for the other two services as needed)
   1. `docker compose -f sandbox.yaml stop` to "turn off" the containers but not delete them.
</details>

### Setting Up Your Team's Repo

**Before you start**: As a team, one person needs to assume the role of _Team Project Repo Owner_.

1. The Team Project Repo Owner needs to **fork** this template repo into their own GitHub account **and give the repo a name consistent with your project's name**. If you're worried that the repo is public, don't. Every team is doing a different project.
1. In the newly forked team repo, the Team Project Repo Owner should go to the **Settings** tab, choose **Collaborators and Teams** on the left-side panel. Add each of your team members to the repository with Write access.

**Remaining Team Members**

1. Each of the other team members will receive an invitation to join.
1. Once you have accepted the invitation, you should clone the Team's Project Repo to your local machine.
1. Set up the `.env` file in the `api` folder based on the `.env.template` file.
1. For running the testing containers (for your team's repo):
   1. `docker compose up -d` to start all the containers in the background
   1. `docker compose down` to shutdown and delete the containers
   1. `docker compose up db -d` only start the database container (replace db with api or app for the other two services as needed)
   1. `docker compose stop` to "turn off" the containers but not delete them.

**Note:** You can also use the Docker Desktop GUI to start and stop the containers after the first initial run.

## Important Tips

1. In general, any changes you make to the api code base (REST API) or the Streamlit app code should be *hot reloaded* when the files are saved.  This means that the changes should be immediately available.  
   1. Don't forget to click the **Always Rerun** button in the browser tab of the Streamlit app for it to reload with changes.
   1. Sometimes, a bug in the code will shut the containers down.  If this is the case, try and fix the bug in the code.  Then you can restart the `app` container in Docker Desktop or restart all the containers with `docker compose restart` (no *-d* flag).
1. The MySQL Container is different. 
   1. When the MySQL container is ***created*** the first time, it will execute any `.sql` files in the `./database-files` folder. **Important:** it will execute them in alphabetical order.  
   1. The MySQL Container's log files are your friend! Remember, you can access them in Docker Desktop by going to the MySQL Container, and clicking on the `Logs` tab.  If there are errors in your .sql files as it is trying to run them, there will be a message in the logs. You can search 🔍 for `Error` to find them more quickly. 
   1. If you need to update anything in any of your SQL files, you **MUST** recreate the MySQL container (rather than just stopping and restarting it).  You can recreate the MySQL container by using the following command: `docker compose down db -v && docker compose up db -d`. 
      1. `docker compose down db -v` stops and deletes the MySQL container and the volume attached to it. 
      1. `docker compose up db -d` will create a new db container and re-run the files in the `database-files` folder. 

## Handling User Role Access and Control

SplitMates uses a simple role-based access control setup in Streamlit without full username/password authentication. The app is organized around three roles:

- **roommate** - normal roommate workflow, including group creation and group dashboards
- **analyst** - analyst views for usage, sessions, and inactive users
- **administrator** - system admin dashboard and admin management pages

### Getting Started with the RBAC

1. The standard Streamlit sidebar navigation is disabled in `app/src/.streamlit/config.toml` so the project can control the links directly.
2. `app/src/modules/nav.py` builds the sidebar dynamically based on the current role stored in `st.session_state`.
3. `app/src/Home.py` provides mock login buttons that switch the user into the roommate or system administrator flows.
4. Every page that needs navigation calls `SideBarLinks()` near the top so the correct links appear for that role.
5. The page prefixes control ordering in the sidebar:
   - `00`-`07` - roommate workflow pages
   - `07`-`09` - analyst pages
   - `20`-`25` - system admin pages


