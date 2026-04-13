# `database-files` Folder

The MySQL server that is running in the db container is set up so that when the container is _created_, any `.sql` files in the `database-files` folder are automatically run. Loosely speaking, the `.sql` files are run in "alphabetical" order. So if your database schema is broken into a few files, it is easiest to rename them with a number at the beginning so they'll be run in the correct order. So, something like `01_db.sql`, `02_db.sql` and so on.

If you make changes to any of the files in the `database-files/` folder AFTER the db container is started, you'll have to delete the container and re-create it for the SQL files to be re-executed. **Note:** simply stopping and re-starting the db container will not re-run the files.

If you are in your sandbox repo, do the following:

```bash
docker compose -f sandbox.yaml down db -v && docker compose -f sandbox.yaml up db
```

If you are working with your team repository, do the following

```bash
docker compose down db -v && docker compose up db -d
```

The `-v` flag will also delete the volume associated with MySQL, which is necessary to rerun the sql files.
