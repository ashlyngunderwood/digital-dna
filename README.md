# Digital DNA

**An end to end data engineering and analytics platform for turning personal music listening history into behavioral insights.**

### Tech Stack

`Python` `PySpark` `Databricks` `Delta Lake` `SQL` `pandas` `REST APIs` `JSON` `Git/GitHub`

### Data Engineering

`ETL Pipelines` `Data Pipelines` `Medallion Architecture` `API Ingestion` `Data Transformation` `Data Validation`

Digital DNA started with a simple question: what does my actual listening history say about my music taste?

I built an end to end data pipeline to answer it. The platform brings together personal Apple Music listening history and external music metadata, then moves that data through ingestion, transformation, validation, enrichment, analytics modeling, and visualization.

The goal is not just to find my most played songs. I want to understand how my taste changes over time, which artists and songs actually define different periods of my life, how quickly I discover and move on from music, and where my perceived favorites differ from my actual listening behavior.

## Architecture

```text
Apple Music Privacy Export                 MusicBrainz API
          |                                      |
          |                              Python Ingestion
          |                                      |
          +------------------+-------------------+
                             |
                             v
                      Databricks / Delta
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
            Bronze         Silver          Gold
          Raw source      Validated       Analytics
             data          records         models
                                             |
                                             v
                                          Power BI
```

The pipeline uses a Bronze, Silver, and Gold medallion architecture. Bronze preserves source data and ingestion context. Silver cleans, standardizes, and validates the data. Gold will combine listening history with enriched metadata into analytics ready models for Power BI.

The layers are organized by stage of processing rather than by source, so Apple Music and MusicBrainz can move through the same architecture and come together downstream.

## Pipeline Today

The first working pipeline handles external music metadata from the MusicBrainz API.

Python ingestion supports both individual and multi track searches while keeping the requested title and artist attached to each response. Saved API samples give me a stable development path when the external API is temporarily unavailable.

Databricks handles the ETL pipeline from there. Bronze ingests the nested JSON response and writes the raw structure to a Delta table. Silver uses PySpark to explode and flatten candidate recordings, validate required fields, compare artist and title information, reject unwanted recording variants, assign match priority, and write the validated dataset to a Silver Delta table.

SQL is used to validate the persisted tables and inspect pipeline outputs independently of the transformation code. Both Bronze and Silver notebooks are built to run cleanly from top to bottom.

## Matching and Data Quality

Music metadata is messy. One search can return the intended studio recording alongside live versions, alternate releases, mixes, commentary, duplicate candidates, and records from another artist.

Instead of assuming the highest API score is automatically the right record, the pipeline applies its own validation rules:

| Priority | Meaning |
| --- | --- |
| 3 | Exact title, correct artist, preferred version |
| 2 | Exact title, correct artist, alternate version |
| 1 | Correct artist with a weaker title variant |
| 0 | Rejected recording variant or artist mismatch |

Match quality and final candidate selection are intentionally separate. More than one record can legitimately meet the highest quality criteria, so the pipeline preserves those candidates for downstream selection instead of forcing an arbitrary match too early.

## Why This Architecture

The personal dataset is small enough that I could process it entirely with pandas. I chose PySpark, Databricks, Delta Lake, and a medallion architecture because I wanted the project to be designed like a scalable data platform rather than a one time analysis.

That also keeps the responsibilities clear. Local Python and Jupyter are used for exploration and testing. Reusable source code handles ingestion, transformation, and validation logic. Databricks handles the persisted ETL pipeline. Delta tables provide the structured data used by downstream SQL, analytics, and BI layers.

## Repository Structure

```text
digital-dna/
├── data/
│   ├── sample/          # Sanitized development samples
│   └── raw/             # Private source data, excluded from Git
├── databricks/          # Bronze and Silver ETL notebooks
├── docs/                # Architecture and project documentation
├── notebooks/           # API exploration and prototyping
├── powerbi/             # Power BI project assets
├── sql/                 # Analytical SQL
└── src/
    ├── ingestion/       # API and source ingestion
    ├── transformation/  # Reusable transformation logic
    └── validation/      # Data quality and matching rules
```

## Data Privacy

My raw Apple Music history is private source data and will not be committed to the public repository. `data/raw/` is excluded from version control, and only sanitized development samples are included in GitHub.

## What's Next

The next phase brings Apple Music listening history into the existing Bronze and Silver pipeline and joins it with enriched MusicBrainz metadata.

From there, Gold will support analytics such as listening eras, song lifecycle, artist loyalty and discovery, repeat behavior, and the difference between claimed favorites and observed listening patterns. Power BI will provide the final interactive reporting layer.

I am also building stronger API fault tolerance so a temporary source failure can be captured without stopping an entire ingestion batch. Incremental ingestion and additional analytical methods can be added as the platform develops.
