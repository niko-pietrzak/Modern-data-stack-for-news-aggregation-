CREATE TABLE IF NOT EXISTS public.newsapi_articles (
    source              VARCHAR(1048),
    author              VARCHAR(1048),
    title               VARCHAR(1048),
    description         VARCHAR(2048),
    url                 VARCHAR(1048),
    urltoimage          VARCHAR(1048),
    publishedat         TIMESTAMP,
    content             TEXT,
    category            VARCHAR(100),
    country             VARCHAR(10),
    ingestion_timestamp TIMESTAMP);

GRANT ALL ON TABLE public.newsapi_articles TO "IAM:airflow-user";
