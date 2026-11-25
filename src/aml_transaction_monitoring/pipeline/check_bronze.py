from pyspark.sql import SparkSession
from pyspark.sql.types import StringType
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
assert row_count == 5078345, "Check A failed: wrong number of rows"

laundering_count = df.filter(df.is_laundering == 1).count()
print("Check B - laundering rows:", laundering_count)
assert laundering_count == 5177, "Check B failed: wrong number of laundering rows"

column_count = len(df.columns)
print("Check C - columns:", column_count)
assert column_count == 11, "Check C failed: wrong number of columns"

print("Check D - from_bank type:", df.schema["from_bank"].dataType)
assert df.schema["from_bank"].dataType == StringType(), "Check D failed: from_bank is not a string"

zero_code_rows = df.filter(df.from_bank == "010").count()
print("Check D - rows with from_bank 010:", zero_code_rows)
assert zero_code_rows > 0, "Check D failed: leading zeros lost in from_bank"

print("All bronze checks passed")

spark.stop()
