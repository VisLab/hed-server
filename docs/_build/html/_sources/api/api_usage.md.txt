# API Endpoints

All services are accessible via REST API endpoints under `/services/`:

| Endpoint | Purpose | Operations |
|----------|---------|------------|
| `/services/strings` | HED string operations | validate, assemble, convert |
| `/services/events` | Event file processing | validate, assemble, search, remodel |
| `/services/schemas` | Schema operations | validate, convert, compare |
| `/services/sidecars` | Sidecar file operations | validate, extract, merge |
| `/services/spreadsheets` | Spreadsheet processing | validate, convert, transform |

## Request/Response Format

### Standard Request Format
```json
{
    "service": "service_name",
    "schema_version": "8.3.0",
    "check_for_warnings": true,
    // Service-specific parameters...
}
```

### Standard Response Format
```json
{
    "error_type": "success",
    "error_msg": "",
    "results": {
        "data": "...",
        "output_display_name": "result.txt",
        "schema_version": "8.3.0",
        // Service-specific results...
    }
}
```

## Error Handling

The API uses consistent error reporting across all services:

- **success** - Operation completed successfully
- **warning** - Operation completed with non-critical issues
- **error** - Operation failed due to validation or processing errors

Error messages include detailed information about what went wrong and how to fix it.

## File Upload Support

Most services support file uploads for batch processing:

### Supported Formats
- **Event files**: TSV, CSV, Excel (.xlsx, .xls)
- **Schema files**: XML, MediaWiki (.mediawiki)
- **Sidecar files**: JSON
- **Spreadsheets**: Excel, CSV, TSV

### File Processing
- Automatic format detection
- Validation before processing
- Detailed error reporting with line numbers
- Result download in original or converted formats

## Common Parameters

Many services share common parameters:

- **schema_version** - HED schema version to use for validation
- **check_for_warnings** - Include non-critical validation warnings
- **expand_defs** - Expand definition tags in output
- **include_description_tags** - Include description metadata
