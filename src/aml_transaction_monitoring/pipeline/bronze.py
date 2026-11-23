from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType

spark = (
    SparkSession.builder
    .appName("aml-bronze")
    .master("local[*]")
    .config("spark.sql.session.timeZone", "UTC")
    .getOrCreate()
)

bronze_schema = StructType([
    StructField("timestamp", StringType(), True),
    StructField("from_bank", StringType(), True),
    StructField("from_account", StringType(), True),
    StructField("to_bank", StringType(), True),
    StructField("to_account", StringType(), True),
    StructField("amount_received", DoubleType(), True),
    StructField('receiving_currency', StringType(), True),
    StructField("amount_paid", DoubleType(), True),
    StructField('payment_currency', StringType(), True),
    StructField("payment_format", StringType(), True),
    StructField("is_laundering", IntegerType(), True),
])

raw_path = "data/raw/HI-Small_Trans.csv"

df = (
    spark.read
    .option("header", "true")
    .schema(bronze_schema)
    .csv(raw_path)
)

df.printSchema()
df.show(5)

bronze_path = "data/bronze/transactions"
df.write.mode("overwrite").parquet(bronze_path)

spark.stop()