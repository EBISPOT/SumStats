# Query Metrics

These scripts contain a series of queries made to run on the cluster to collect metrics on query times.

query_report.sh is the *only script* that needs to be run, and it will execute all the others and gather metrics.

There are 6 categories of queries run:

1. query_report_chr queries for chromosome 1
2. query_report_chrbp queries for chromosome 1 with a specific base pair location region
3. query_report_pvallower queries for chromosome 1 while setting a lower p-value threshold
4. query_report_pvalrange queries for chromosome 1 while setting a lower and upper p-value threshold
5. query_report_non_existing queries for a variant id that does not exist and counts how much time it would take look into all the chromosomes and not find it
6. query_report_var<x> queries for a specific variant (a) specifying it's chromosome (b) specifying it's chromosome and filtering by study accession (c) not specifying chromosome which results in a lookup in all chromosomes until found


All the chromosome queries are repeated with different starting points (start 0...10000000).

query_metrics.sh is responsible for parsing the job output files and gathering the metrics.

In order for them to run, you will need to create a properties.json file and place it in the same directory as the scripts.