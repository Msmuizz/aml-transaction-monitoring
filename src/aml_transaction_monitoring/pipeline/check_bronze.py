from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("aml-check-bronze")
    .master("local[*]")
    .config("spark.sql.session.timeZone", "UTC")
    .getOrCreate()
)

bronze_path = "data/bronze/transactions"
df = spark.read.parquet(bronze_path)

row_count = df.count()
print("Check A - rows:", row_count)

laundering_count = df.filter(df.is_laundering == 1).count()
print("Check B - laundering rows:", laundering_count)

column_count = len(df.columns)
print("Check C - columns:", column_count)

print("Check D - from_bank type:", df.schema["from_bank"].dataType)

zero_code_rows = df.filter(df.from_bank == "010").count()
print("Check D - rows with from_bank 010:", zero_code_rows)


spark.stop()
