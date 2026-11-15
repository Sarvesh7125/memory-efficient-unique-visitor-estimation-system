SELECT
  user_pseudo_id,
  FORMAT_TIMESTAMP('%Y-%m-%dT%H:%M:%SZ', TIMESTAMP_MICROS(event_timestamp), 'UTC') AS timestamp,
  COALESCE((SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'page_location' LIMIT 1), '') AS page_url,
  event_name AS event_type
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20201107'
  AND user_pseudo_id IS NOT NULL;
