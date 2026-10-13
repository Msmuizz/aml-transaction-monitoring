from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("aml-spark-check")
    .master("local[*]")
    .config("spark.sql.session.timeZone", "UTC")
    .getOrCreate()
)

print("Spark version:", spark.version)
df = spark.createDataFrame([(1, "a"), (2, "b")], ["id", "value"])
df.show()
spark.stop()
