import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.transforms import *

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = glueContext.create_dynamic_frame.from_catalog(
    database="housing_db", 
    table_name="housing_data"
)

# Extract the data
housing_dyf = glueContext.create_dynamic_frame.from_catalog(
    database="housing_db",
    table_name="housing_data"
)

# Transform the data
# Remove null values
housing_cleaned = housing_dyf.filter(f=lambda row: row["price"] is not None and row["sqft_living"] is not None)

# Add derived columns (e.g., price per square foot)
housing_transformed = housing_cleaned.map(
    lambda row: {
        **row,
        "price_per_sqft": row["SalePrice"] / row["LotArea"]
    }
)

# Convert DynamicFrame back to Spark DataFrame
housing_df = housing_transformed.toDF()

# Write the transformed data to S3 in Parquet format
output_path = "s3://rlm-dev-playground/output/housing_cleaned"
housing_df.write.mode("overwrite").parquet(output_path)
