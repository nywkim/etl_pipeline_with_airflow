import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql import functions as SqlFuncs

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node S3 bucket
S3bucket_node1 = glueContext.create_dynamic_frame.from_catalog(
    database="spotify", table_name="logs", transformation_ctx="S3bucket_node1"
)

# Script generated for node Change Schema (Apply Mapping)
ChangeSchemaApplyMapping_node1672155019273 = ApplyMapping.apply(
    frame=S3bucket_node1,
    mappings=[
        ("track_id", "string", "track_id", "string"),
        ("track_name", "string", "track_name", "string"),
        ("artist_id", "string", "artist_id", "string"),
        ("artist_name", "string", "artist_name", "string"),
    ],
    transformation_ctx="ChangeSchemaApplyMapping_node1672155019273",
)

# Script generated for node Change Schema (Apply Mapping)
ChangeSchemaApplyMapping_node1672154827037 = ApplyMapping.apply(
    frame=S3bucket_node1,
    mappings=[
        ("day", "string", "day", "string"),
        ("hour", "long", "hour", "string"),
        ("track_id", "string", "track_id", "string"),
    ],
    transformation_ctx="ChangeSchemaApplyMapping_node1672154827037",
)

# Script generated for node ApplyMapping
ApplyMapping_node2 = ApplyMapping.apply(
    frame=S3bucket_node1,
    mappings=[
        ("track_id", "string", "track_id", "string"),
        ("acousticness", "double", "acousticness", "double"),
        ("danceability", "double", "danceability", "double"),
        ("energy", "double", "energy", "double"),
        ("liveness", "double", "liveness", "double"),
        ("loudness", "double", "loudness", "double"),
        ("instrumentalness", "string", "instrumentalness", "double"),
        ("speechiness", "double", "speechiness", "double"),
        ("tempo", "double", "tempo", "double"),
        ("valence", "double", "valence", "double"),
        ("`duration(ms)`", "long", "`duration(ms)`", "long"),
        ("mode", "long", "mode", "long"),
        ("key", "long", "key", "long"),
    ],
    transformation_ctx="ApplyMapping_node2",
)

# Script generated for node Drop Duplicates
DropDuplicates_node1674637918704 = DynamicFrame.fromDF(
    ChangeSchemaApplyMapping_node1672155019273.toDF().dropDuplicates(["track_id"]),
    glueContext,
    "DropDuplicates_node1674637918704",
)

# Script generated for node S3 bucket
S3bucket_node3 = DynamicFrame.fromDF(
    ApplyMapping_node2.toDF().dropDuplicates(["track_id"]),
    glueContext,
    "S3bucket_node3",
)

# Script generated for node Amazon S3
AmazonS3_node1674145529368 = glueContext.getSink(
    path="s3://airflow-nk/data/listened/",
    connection_type="s3",
    updateBehavior="LOG",
    partitionKeys=[],
    compression="snappy",
    enableUpdateCatalog=True,
    transformation_ctx="AmazonS3_node1674145529368",
)
AmazonS3_node1674145529368.setCatalogInfo(
    catalogDatabase="spotify", catalogTableName="records"
)
AmazonS3_node1674145529368.setFormat("glueparquet")
AmazonS3_node1674145529368.writeFrame(ChangeSchemaApplyMapping_node1672154827037)
# Script generated for node Amazon S3
AmazonS3_node1674145222218 = glueContext.getSink(
    path="s3://airflow-nk/data/trackId/",
    connection_type="s3",
    updateBehavior="LOG",
    partitionKeys=[],
    compression="snappy",
    enableUpdateCatalog=True,
    transformation_ctx="AmazonS3_node1674145222218",
)
AmazonS3_node1674145222218.setCatalogInfo(
    catalogDatabase="spotify", catalogTableName="tracks"
)
AmazonS3_node1674145222218.setFormat("glueparquet")
AmazonS3_node1674145222218.writeFrame(DropDuplicates_node1674637918704)
# Script generated for node Amazon S3
AmazonS3_node1674145664621 = glueContext.getSink(
    path="s3://airflow-nk/data/music/",
    connection_type="s3",
    updateBehavior="LOG",
    partitionKeys=[],
    compression="snappy",
    enableUpdateCatalog=True,
    transformation_ctx="AmazonS3_node1674145664621",
)
AmazonS3_node1674145664621.setCatalogInfo(
    catalogDatabase="spotify", catalogTableName="musics"
)
AmazonS3_node1674145664621.setFormat("glueparquet")
AmazonS3_node1674145664621.writeFrame(S3bucket_node3)
job.commit()
