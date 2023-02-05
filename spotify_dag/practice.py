from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.providers.amazon.aws.operators.athena import AthenaOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
import boto3

default_args = {
    'owner' : 'airflow',
    'depends_on_past' : False,
    'start_date' : datetime(2023, 1, 29, 17, 0, 0),
    'email' : ['nywkim@example.com'],
    'email_on_failure' : False,
    'email_on_retry' : False,
    'retries' : 1,
    'retry_delay' : timedelta(minutes=1)
}

dag = DAG(
    'Spotify_etl_2',
    default_args=default_args,
    description='Spotify Gold ETL',
    schedule_interval=timedelta(days=1),
)

athena_agg = AthenaOperator(
    task_id="athena_agg",
    database="spotify",
    query="""
        INSERT INTO listen_record_by_artist_test
        SELECT artist_name, day, count(*) as listen_count
        FROM (SELECT day, track_id FROM spotify.records where day='{{ds}}') a
            JOIN (SELECT DISTINCT(track_id) as track_id, artist_name FROM spotify.tracks) b
            ON a.track_id=b.track_id
        group by artist_name,day
        order by listen_count desc;
    """,
    output_location="s3://airflow-nk/sample/",
    dag=dag,
)

def delete_files() :
    s3_client = boto3.client('s3')

    response = s3_client.list_objects_v2(Bucket='airflow-nk', Prefix='logs/')

    for object in response['Contents']:
        print('Deleting', object['Key'])
        s3_client.delete_object(Bucket=BUCKET, Key=object['Key'])


delete_bronze_logs = PythonOperator(
    task_id='delete_bronze_logs',
    python_callable=delete_files,
    dag=dag,
)

s3_to_redshift = S3ToRedshiftOperator(
    task_id='s3_to_redshift',
    schema='dev.spotify',
    table='listen_records_by_artists',
    s3_bucket='airflow-nk',
    s3_key='data/listen_records_by_artists_test',
    copy_options=["FORMAT AS PARQUET"],
    method='UPSERT',
    upsert_keys=['day'],
    dag=dag,
)

athena_agg >> delete_bronze_logs >> s3_to_redshift
