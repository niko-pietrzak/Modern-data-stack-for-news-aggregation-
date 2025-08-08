-- models/base_newsapi_articles.sql

{{ config(materialized='view') }}

SELECT *
FROM dev.public.newsapi_articles
