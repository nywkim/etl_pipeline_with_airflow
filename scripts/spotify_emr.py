import sys
from pyspark.sql.functions import *
from pyspark.sql import SparkSession



if __name__ == "__main__":

    spark = SparkSession\
        .builder\
        .appName("SpotifyAgg")\
        .getOrCreate()

    output_path = None

    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    else:
        print("S3 output location not specified printing top 10 results to output stream")

    parquet_1 = spark.read.parquet("s3://airflow-nk/data/listened/")
    parquet_1.createOrReplaceTempView("records")
    parquet_2 = spark.read.parquet("s3://airflow-nk/data/trackId/")
    parquet_2.createOrReplaceTempView("tracks")   
    df = spark.sql("select track_name, listened\
                    from (select track_id, count(*) as listened from records group by track_id order by listened desc) as a \
                    left join (select distinct(track_id) as track_id, track_name from tracks) as b \
                    on a.track_id=b.track_id\
                    where listened>1;")


    if output_path:
        df.write.mode("overwrite").csv(output_path)
        print("SpotifyAgg job completed successfully. Refer output at S3 path: " + output_path)
    else:
        df.show(10, False)
        print("SpotifyAgg job completed successfully.")

    spark.stop()