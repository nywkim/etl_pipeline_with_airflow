from datetime import timedelta, datetime
from airflow import DAG
from airflow.providers.amazon.aws.operators.emr import (
    EmrServerlessCreateApplicationOperator,
    EmrServerlessDeleteApplicationOperator,
    EmrServerlessStartJobOperator,
)
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
import boto3

APPLICATION_ID = "00f8ipvjpu1aqp2q"
ROLE_ARN_KEY = "arn:aws:iam::725381868002:role/AmazonEMR-ExecutionRole-1678813753771"
S3_BUCKET = "airflow-nk"
SPARK_CONFIGURATION_OVERRIDES = {
    "monitoringConfiguration":{
        "s3MonitoringConfiguration":{"logUri":f"s3://{S3_BUCKET}/emr-serverless/"}
    },
}

with DAG(
    dag_id="spotify_dag_3",
    schedule=None,
    start_date=datetime(2021, 1, 1),
    tags=["example"],
    catchup=False,
) as dag:
    emr_serverless_app = EmrServerlessCreateApplicationOperator(
        task_id="create_emr_spark_app",
        release_label="emr-6.6.0",
        job_type="SPARK",
        config={"name": "spark-agg"},
    )

    application_id = emr_serverless_app.output

    start_job = EmrServerlessStartJobOperator(
        task_id="emr_serverless_job",
        application_id=application_id,
        execution_role_arn=ROLE_ARN_KEY,
        job_driver={
            "sparkSubmit": {
                "entryPoint": f"s3://{S3_BUCKET}/scripts/spotify_emr.py",
                "entryPointArguments": [f"s3://{S3_BUCKET}/emr-serverless-spark/output"],
                "sparkSubmitParameters": "--conf spark.executor.cores=1 --conf spark.executor.memory=4g\
                    --conf spark.driver.cores=1 --conf spark.driver.memory=4g --conf spark.executor.instances=1\
                    --conf spark.hadoop.hive.metastore.client.factory.class=com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory",
            }
        },
        configuration_overrides=SPARK_CONFIGURATION_OVERRIDES,
    )

    delete_app = EmrServerlessDeleteApplicationOperator(
        task_id="delete_emr_spark_app",
        application_id=application_id,
    )

    (emr_serverless_app >> start_job >> delete_app)