from pyspark.sql import SparkSession

def test_spark():
    print("Testing Spark Mongo Connector 10.3.0")
    spark = SparkSession.builder \
        .appName("PNCP_Test") \
        .config("spark.mongodb.read.connection.uri", "mongodb://localhost/test.test") \
        .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.3.0") \
        .getOrCreate()
    try:
        df = spark.read.format("mongodb").load()
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_spark()
