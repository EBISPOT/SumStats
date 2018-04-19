# Final formatter for loading summary statistics database

The formatter brings pre-formatted summary statistics files to a database-loadable format.

Files must first be formatted using the sum-stats-formatter, bringing them to a common but not database-loadable format.
This final formatter, replaces headers with database-loadable headers and adds any required headers that are missing. Where a header has been added, the records are populated with 'NA' values.