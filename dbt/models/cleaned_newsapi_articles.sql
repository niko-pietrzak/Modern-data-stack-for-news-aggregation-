-- models/cleaned_newsapi_articles.sql

{{ config(materialized='table') }}

SELECT
    TRIM(json_extract_path_text(source, 'name')) AS source_name,
    TRIM(author)                   AS author_name,
    TRIM(LOWER(title))             AS title,
    TRIM(description)              AS description,
    url,
    publishedat::DATE              AS published_date,
    content,
    LOWER(category)                AS category,
    LOWER(country)                 AS country_code,
    ingestion_timestamp
FROM {{ ref('base_newsapi_articles') }}
WHERE title IS NOT NULL

