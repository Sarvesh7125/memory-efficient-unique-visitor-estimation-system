# Dataset documentation

## Real source A: UCI Clickstream Data for Online Shopping
Source: https://archive.ics.uci.edu/dataset/553/clickstream+data+for+online+shopping
DOI: https://doi.org/10.24432/C5QK7X
Citation: Clickstream Data for Online Shopping [Dataset]. (2019). UCI Machine Learning Repository.
License: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
Published size: 165,474 records, 14 features; April–August 2008. Actual local counts are not verified until the acquisition script runs. The download was blocked by DNS in the build environment; no actual real records are bundled.
Each row is a click. The identifier is a session ID, not a stable person ID. The project labels results from this source as distinct sessions. Transformations: date assembled from year/month/day (no clock time supplied), product code converted to a constructed path, event type set to click. Duplicate visits are preserved.

## Realistic user-level alternative: Google GA4 obfuscated ecommerce sample
Source: https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset
Public BigQuery dataset, Nov 2020–Jan 2021. Export query in ga4_export.sql selects one week; actual row count is recorded after export. Requires Google Cloud/BigQuery access; no export is bundled. Pseudonymous user IDs approximate visitors, not people. Google notes obfuscation and placeholder values. Use subject to source terms; do not assume a redistribution license.

## Synthetic benchmark source
Generated locally with NumPy seed 42; exactly 25% distinct IDs per file. Every intended ID occurs at least once, remaining events sample uniformly from those IDs and are shuffled. Independent sizes (not nested); timestamps are sequential synthetic values, and pages/events sampled independently (no realistic funnel implied). Source and exact counts in data/benchmark/manifest.json. These are not real logs.

## Canonical schema
visitor_id (string), timestamp (source date or timestamp), page_url (observed or constructed), event_type (string). Blank and placeholder IDs are rejected; repeats preserved. ID strings are trimmed but not converted to integers. Missing timestamps rejected by normalization; non-UCI timestamp strings are retained as supplied, not comprehensively validated.
