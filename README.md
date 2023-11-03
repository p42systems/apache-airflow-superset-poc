# Apache Airflow & Superset POC

## Current status

- [x] Airflow containers configured
- [ ] Database for data storage (not used for metadata) container configured
- [ ] Superset containers configured

## Quick Start

> Warning: Airflow uses a lot of resources and some commands might take a while to run.

### Step 1

> If using `podman-compose` set `AIRFLOW_UID` to `1`

Create `.env` file
```bash
# This command will create the file for you
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

The file should look something like this:
```
AIRFLOW_UID=1000
```

### Step 2

Build the images
```bash
docker compose build
```

### Step 3

> Very important step! If something goes wrong then a full clean might be required with `docker compose down -v`. `-v` removes the volumes. 

Initialize the database
```bash
docker compose airflow-init
```

### Step 4

Start all the containers
```bash
docker compose up -d
```

The website should be available at `localhost:8080`. Username and password are `airflow`
