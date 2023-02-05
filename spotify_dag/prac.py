from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.providers.amazon.aws.operators.athena import AthenaOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.amazon.aws.operators.s3 import S3DeleteObjectsOperator
import boto3

default_args = {
    'owner' : 'airflow',
    'depends_on_past' : False,
    'start_date' : datetime(2023, 1, 30, 17, 0, 0),
    'email' : ['nywkim@example.com'],
    'email_on_failure' : False,
    'email_on_retry' : False,
    'retries' : 1,
    'retry_delay' : timedelta(minutes=1)
}

S3_BUCKET_NAME = "airflow-nk"

dag = DAG(
    'spotify_dag_prac',
    default_args=default_args,
    description='My Spotify account ETL',
    schedule_interval=timedelta(days=1),
)

def delete_files() :
    s3_client = boto3.client('s3')

    BUCKET = 'airflow-nk'
    PREFIX = 'logs/'

    response = s3_client.list_objects_v2(Bucket=BUCKET, Prefix=PREFIX)

    for object in response['Contents']:
        print('Deleting', object['Key'])
        s3_client.delete_object(Bucket=BUCKET, Key=object['Key'])

delete_s3bucket_files = PythonOperator(
  task_id='delete_s3bucket_files',
  python_callable=delete_files,
  dag=dag,
)

delete_s3bucket_files
