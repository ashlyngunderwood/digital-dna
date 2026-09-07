# Databricks notebook source
spark.sql("""
    CREATE SCHEMA IF NOT EXISTS workspace.digital_dna_silver
""")

# COMMAND ----------

bronze_df = spark.table(
    "workspace.digital_dna_bronze.musicbrainz_raw"
)

bronze_df.printSchema()

# COMMAND ----------

recording_count = (
    bronze_df
    .selectExpr(
        "sum(size(api_response.recordings)) AS recording_count"
    )
    .first()["recording_count"]
)

if recording_count == 0:
    raise ValueError(
        "No MusicBrainz recording candidates found in Bronze."
    )

print(f"Bronze recording candidates: {recording_count}")

# COMMAND ----------

from pyspark.sql.functions import explode

silver_exploded_df = (
    bronze_df
    .select(
        "requested_title",
        "requested_artist",
        explode("api_response.recordings").alias("recording")
    )
)

display(silver_exploded_df)

# COMMAND ----------

silver_df = silver_exploded_df.select(
    "requested_title",
    "requested_artist",
    silver_exploded_df["recording.id"].alias("recording_id"),
    silver_exploded_df["recording.title"].alias("title"),
    silver_exploded_df["recording.artist-credit"][0]["artist"]["name"].alias("artist"),
    silver_exploded_df["recording.score"].alias("score"),
    silver_exploded_df["recording.first-release-date"].alias("first_release_date"),
    silver_exploded_df["recording.disambiguation"].alias("disambiguation")
)

display(silver_df)

# COMMAND ----------

from pyspark.sql.functions import col

missing_required_fields = (
    silver_df
    .filter(
        col("title").isNull()
        | col("artist").isNull()
    )
    .count()
)

if missing_required_fields > 0:
    raise ValueError(
        f"{missing_required_fields} records are missing "
        "required title or artist fields."
    )

print("Required matching fields validated.")

# COMMAND ----------

from pyspark.sql.functions import (
    lower,
    trim,
    coalesce,
    lit,
    regexp_replace,
    when
)

silver_validated_df = (
    silver_df
    .withColumn(
        "normalized_disambiguation",
        lower(
            regexp_replace(
                coalesce(col("disambiguation"), lit("")),
                "‐",
                "-"
            )
        )
    )
    .withColumn(
        "rejection_reason",
        when(
            col("normalized_disambiguation").contains("live"),
            lit("Excluded variant: live")
        )
        .when(
            col("normalized_disambiguation").contains("dj-mix"),
            lit("Excluded variant: dj-mix")
        )
        .when(
            col("normalized_disambiguation").contains("lyric video"),
            lit("Excluded variant: lyric video")
        )
        .when(
            col("normalized_disambiguation").contains("commentary"),
            lit("Excluded variant: commentary")
        )
    )
    .withColumn(
        "match_priority",
        when(
            col("rejection_reason").isNotNull(),
            0
        )
        .when(
            lower(trim(col("artist")))
            != lower(trim(col("requested_artist"))),
            0
        )
        .when(
            (
                lower(trim(col("title")))
                == lower(trim(col("requested_title")))
            )
            & (col("normalized_disambiguation") == ""),
            3
        )
        .when(
            lower(trim(col("title")))
            == lower(trim(col("requested_title"))),
            2
        )
        .otherwise(1)
    )
)

display(silver_validated_df)

# COMMAND ----------

silver_validated_df \
    .groupBy(
        "requested_title",
        "requested_artist",
        "match_priority"
    ) \
    .count() \
    .orderBy(
        "requested_title",
        "match_priority"
    ) \
    .show(truncate=False)

# COMMAND ----------

print("Silver row count:", silver_validated_df.count())

silver_validated_df.groupBy("match_priority") \
    .count() \
    .orderBy("match_priority") \
    .show()

# COMMAND ----------

silver_validated_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(
        "workspace.digital_dna_silver.musicbrainz_recordings"
    )

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     requested_title,
# MAGIC     requested_artist,
# MAGIC     recording_id,
# MAGIC     title,
# MAGIC     artist,
# MAGIC     score,
# MAGIC     first_release_date,
# MAGIC     disambiguation,
# MAGIC     rejection_reason,
# MAGIC     match_priority
# MAGIC FROM workspace.digital_dna_silver.musicbrainz_recordings
# MAGIC ORDER BY
# MAGIC     requested_title,
# MAGIC     match_priority DESC,
# MAGIC     score DESC;