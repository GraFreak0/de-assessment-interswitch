# Apache Airflow Data Pipeline

## Overview
This project implements an Apache Airflow data pipeline for fetching trip metrics from ClickHouse, processing the data, and storing it in an SQLite database. The pipeline is orchestrated using Airflow DAGs and consists of two main tasks:

1. **Fetch Trip Metrics**: Retrieves data from ClickHouse via an HTTP API.
2. **Load Data into SQLite**: Processes and stores the data in an SQLite database.

## Pipeline Workflow
1. **Extract**: Fetch trip metrics from ClickHouse.
2. **Transform**: Process the data and assign appropriate column names.
3. **Load**: Store the structured data in an SQLite database.

## Project Structure
```
root/
│── airflow/
│   │── dags/ 
│   │   └── trip_metrics_dag.py  # Airflow DAG script
│   │── db/
│   │   └── clickHouseQuery.sql  # Clickhouse Query
│   │── airflow.cfg               # Airflow configuration file
│   │── airflow.db               # Airflow db file
│   │── standalone_admin_password.txt    # Airflow admin password
│   │── trip_metrics.db       # Trip metrics SQLite DB
│   └── webserver_config.py   # Webserver Configuration File
│── docker-compose.yaml       # YAML File for Docker Compose
│── requirements.txt          # Python dependencies
│── README.md                 # Project documentation
└── Dockerfile                # Dockerfile for building the image
```

## Prerequisites
Before running the Airflow pipeline, ensure the following dependencies are installed:

- **Apache Airflow**
- **Python 3.9+**
- **SQLite**
- **ClickHouse (HTTP API Enabled)**
- **Docker Desktop**
- **VS Code** (install `Docker` extension for VS Code)
- **Required Python Packages** (see `requirements.txt`)

## Airflow Configuration

### Build Airflow Image & Install Dependencies

#### Method 1: Using Docker extension
1. Open Repository on VS Code
2. Find and right-click on `Dockerfile`then select `Build Image`
Note: This will build the Docker image with the required dependencies.

#### Method 2: Using Inteegrated Terminal CLI
1. Open Repository on VS Code
2. Right-click on the empty space below the folders and files and select `Òpen in Integrated Terminal`
3. In the terminal type `docker build -t apache-airflow:latest .`
Note: This will build the Docker image with the required dependencies.

### Start Services in `docker-compose.yaml` file
- Right-click on the docker-compose.yaml file and select `Compose up`

OR 

- Open the terminal and navigate to the project directory
- Type `docker-compose up -d` to start the services in detached mode.
Note: This initializes all services includin the scheduler and webserver.

### Airflow Configuration File (`airflow.cfg`)
Ensure the configuration file is set up with the appropriate executor and database settings.

### Access the Webserver
- Open a web browser and navigate to `http://localhost:8080`
- Use the admin credentials from `standalone_admin_password.txt` to login
    - Username: `admin`
Note: incase the services are running and the webserver is not up, see `Troubleshooting the Webserver` section below

### Setup ClickHouse DB Connection
- In the Airflow web interface, navigate to Admin > Connections
- Create a new connection with the following details:
    - Conn Id: `clickhouse_default`
    - Conn Type: `HTTP`
    - Host: `https://github.demo.trial.altinity.cloud`
    - Port: `8443`
    - Username: `demo`
    - Password: `demo`

### Create your DAG file
- Create a new folder under the `airflow` folder and name it `dags`
- Create a new DAG file inside the `dags` folder and name it with extension.py e.g `trip_metrics_dag.py`
- Write your DAG logic inside the DAG file.

### Initialize DAG Pipelines
#### Method 1: Using Airflow Webserver
- In the Airflow web interface, navigate to DAGs
- You should see the list of dags pipelines in the container
- Click on the `trip_metrics_pipeline`
- Trigger DAG using the `Trigger DAG`(Play sign) button at the top right corner of the DAG page
- Switch to Graph mode to monitor the DAG execution
- You can also check logs for the tasks by selecting the task and Clicking on the `View Logs` button

#### Method 2: Using Airflow CLI in Docker
- Trigger the DAG
```bash
airflow dags list
airflow dags trigger trip_metrics_pipeline
```
- Monitor the DAG execution and Logs
```bash
airflow tasks logs trip_metrics_pipeline fetch_trip_metrics
```

### Troubleshooting the Webserver
#### Using Docker CLI
- Check the logs of the webserver container to see if there are any errors
- If the webserver is not up, try to restart the webserver container
```bash
docker-compose up -d webserver
```

OR
- Clck on the `Show container actions` button and select `Open in Terminal`
- This should open the airflow container in terminal `(airflow)`
- Run the following command to verify start the webserver
```bash
airflow webserver
```
- This should start the webserver else give an error.
- If the error is an `Error: Already running on PID 37 (or pid file '/opt/airflow/airflow-webserver.pid' is stale)`
- This means the existing webserver is still running or is stale, so you can either restart the container or webserver. I personally will remove the existing webserver configuration file and restart the webserver using below
```bash
rm -f /opt/airflow/airflow-webserver.pid
airflow webserver --port 8080
```

###
## Conclusion
This pipeline automates data extraction from ClickHouse and storage in SQLite using Apache Airflow. It ensures a structured workflow for data processing and storage.