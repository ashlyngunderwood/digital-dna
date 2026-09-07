# Databricks notebook source
spark.sql("""
    CREATE SCHEMA IF NOT EXISTS workspace.digital_dna_bronze
    """)

# COMMAND ----------

source_path = "/Volumes/workspace/digital_dna_bronze/source_files/musicbrainz_multi_track_sample.json"

bronze_df = (
    spark.read
    .option("multiline", "true")
    .json(source_path)
)

bronze_df.printSchema()

# COMMAND ----------

bronze_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(
        "workspace.digital_dna_bronze.musicbrainz_raw"
    )

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     requested_title,
# MAGIC     requested_artist,
# MAGIC     api_response.count AS total_matches,
# MAGIC     size(api_response.recordings) AS recording_count
# MAGIC FROM workspace.digital_dna_bronze.musicbrainz_raw 