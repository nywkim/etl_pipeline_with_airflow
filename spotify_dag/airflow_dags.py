from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.amazon.aws.operators.glue_crawler import GlueCrawlerOperator
from airflow.utils.dates import days_ago
from spotify_dags import token_refresh, find_songs, GlueJobRun

default_args = {
    'owner' : 'airflow',
    'depends_on_past' : False,
    'start_date' : days_ago(0,0,0,0,0),
    'email' : ['nywkim@example.com'],
    'email_on_failure' : False,
    'email_on_retry' : False,
    'retries' : 1,
    'retry_delay' : timedelta(minutes=1)
}

dag = DAG(
    'spotify_dag',
    default_args=default_args,
    description='My Spotify account ETL',
    schedule_interval=timedelta(hours=2),
)

start = DummyOperator(task_id="start", dag=dag)

run_etl = BranchPythonOperator(
	task_id='spotify_etl',
	python_callable=find_songs,
	op_kwargs={
		"year": "{{ execution_date.year }}",
		"month": "{{ execution_date.month }}",
		"day": "{{ execution_date.day }}",
		"hour": "{{ execution_date.hour }}"
	},
	dag=dag,
)

etl_start = DummyOperator(task_id="etl_start", dag=dag)

break_time = DummyOperator(task_id="break_time", dag=dag)

glue_crawler_config = {"Name": "spotify-crawl"}

crawl_s3 = GlueCrawlerOperator(
    task_id="crawl_s3",
    config=glue_crawler_config,
    dag=dag
)

glue_job = PythonOperator(
    task_id='glue_job',
    python_callable=GlueJobRun,
    dag=dag,
)

start >> run_etl
run_etl >> [etl_start, break_time]
etl_start >> crawl_s3 >> glue_job
