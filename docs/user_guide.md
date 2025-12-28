# HED online tools user guide

This guide provides comprehensive instructions for using the HED web-based tools and REST API services for validation, transformation, and analysis of HED annotations.

## Quick links

- 🌐 [HED online tools](https://hedtools.org/hed)
- 📚 [API reference](api/index.html)
- 🐛 [GitHub issues](https://github.com/hed-standard/hed-web/issues)
- 🎓 [HED resources](https://www.hedtags.org/hed-resources)
- 📖 [HED tpecification](https://www.hedtags.org/hed-specification)
- 🐍 [Python HEDTools](https://www.hedtags.org/hed-python)

## Table of contents

1. [Getting started](#getting-started)
2. [Working with events files](#working-with-events-files)
3. [Working with sidecars](#working-with-sidecars)
4. [Working with spreadsheets](#working-with-spreadsheets)
5. [Working with HED strings](#working-with-hed-strings)
6. [Working with HED schemas](#working-with-hed-schemas)
7. [Using RESTful services](#using-restful-services)
8. [Best practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Getting started

### Accessing HED online tools

HED web-based tools are available directly through a browser at [https://hedtools.org/hed](https://hedtools.org/hed). These tools are free to use and don't require a login. Two versions are available:

- **Production**: [https://hedtools.org/hed](https://hedtools.org/hed) - Stable release version
- **Development**: [https://hedtools.org/hed_dev](https://hedtools.org/hed_dev) - Latest development features

### Tool organization

The HED browser-based tools are organized into the following pages:

| Tool             | URL                                           | Description                                                                 |
| ---------------- | --------------------------------------------- | --------------------------------------------------------------------------- |
| **Events**       | [link](https://hedtools.org/hed/events)       | Validation, summary, search, and generation tools for tabular (.tsv) files  |
| **Sidecars**     | [link](https://hedtools.org/hed/sidecars)     | Validation, transformation, extraction, and merging tools for JSON sidecars |
| **Spreadsheets** | [link](https://hedtools.org/hed/spreadsheets) | Validation and transformation tools for spreadsheet files                   |
| **Strings**      | [link](https://hedtools.org/hed/strings)      | Quick validation and transformation of individual HED strings               |
| **Schemas**      | [link](https://hedtools.org/hed/schemas)      | Validation, conversion, and comparison tools for HED schemas                |

### Common features

#### Schema selection

Most tools require you to specify a HED schema version. You can:

- **Select a standard version**: Use the pull-down menu to choose from official HED releases
- **Upload a custom schema**: Select "Other" and upload your own HED schema file

The tool automatically caches standard schemas for faster processing.

#### Tag formats

HED supports three tag formats:

- **Short form**: Only the leaf node (e.g., `Red`)
- **Long form**: Full path from root (e.g., `Property/Sensory-property/.../Red`)
- **Intermediate form**: Partial path (e.g., `Color/Red`)

All HED tools handle any combination of these formats.

#### Definition expansion

Many tools have an `Expand defs` option that replaces `Def/xxx` tags with expanded definitions in the form `(Def-expand/xxx, yyy)` where `yyy` is the actual definition content.

## Working with events files

Events files are BIDS-style tab-separated value (TSV) files with a header line giving column names. These columns map to metadata in accompanying JSON sidecars.

### Validate an events file

Validates HED annotations in a BIDS events file, useful for debugging during annotation development.

**Steps:**

1. Select the `Validate` action
2. Toggle `Check for warnings` if you want to include warnings
3. Select the HED version
4. Optionally upload a JSON sidecar file (`.json`)
5. Upload an events file (`.tsv`)
6. Click the `Process` button

**Returns:** A downloadable `.txt` file of error messages if errors are found.

**Note:** This tool validates a single events file. For full BIDS dataset validation with inherited sidecars and library schemas, use the [Python tools](https://hed-python.readthedocs.io/).

### Assemble annotations

Produces a file with fully assembled HED annotations for each event, combining sidecar and column values.

**Steps:**

1. Select the `Assemble annotations` action
2. Toggle `Expand defs` if you want expanded definitions
3. Select the HED version
4. Optionally upload a JSON sidecar file (`.json`)
5. Upload the events file (`.tsv`)
6. Click the `Process` button

**Returns:** A downloadable `.tsv` file with two columns: onset times and assembled HED strings.

### Search annotations

Search for events matching specific HED criteria within an events file.

**Steps:**

1. Select the `Search annotations` action
2. Enter your search query using HED tags
3. Select the HED version
4. Optionally upload a JSON sidecar file (`.json`)
5. Upload the events file (`.tsv`)
6. Click the `Process` button

**Returns:** A downloadable `.tsv` file containing only the rows matching your search criteria.

### Generate sidecar template

Creates a JSON sidecar template from an events file, ready to be filled with HED annotations.

**Steps:**

1. Select the `Generate sidecar template` action
2. Upload the events file (`.tsv`)
3. Review the column list that appears
4. In the left checkboxes, select columns to include in the template
5. In the right checkboxes, select columns requiring individual value annotations
6. Click the `Process` button

**Returns:** A downloadable `.json` sidecar template file.

**Tip:** For datasets with multiple events files, use the Python tools to generate a template based on all files.

### Execute remodel script

Apply table remodeling operations to transform or summarize events files without programming.

**Steps:**

1. Select the `Execute remodel script` action
2. Toggle `Include summaries` if you want summary output
3. Select the HED version
4. Upload a JSON remodel script file
5. Optionally upload a JSON sidecar file (`.json`)
6. Upload the events file (`.tsv`)
7. Click the `Process` button

**Returns:** A zip archive containing transformed events file and summaries.

See the [Table remodeler documentation](https://www.hedtags.org/table-remodeler) for details on creating remodel scripts.

## Working with sidecars

BIDS JSON sidecars (files ending in `events.json`) contain metadata and HED annotations for BIDS datasets.

### Validate a sidecar

Validates HED annotations in a JSON sidecar file.

**Steps:**

1. Select the `Validate` action
2. Toggle `Check for warnings` if you want warnings
3. Select the HED version
4. Upload a JSON sidecar file (`.json`)
5. Click the `Process` button

**Returns:** A downloadable `.txt` file of error messages if errors are found.

**Note:** For sidecars with external definitions or library schemas, use the Python tools for complete validation.

### Convert sidecar to long

Converts all HED tags in a sidecar to long form (full paths).

**Steps:**

1. Select the `Convert to long` action
2. Toggle `Expand defs` if you want expanded definitions
3. Select the HED version
4. Upload the JSON sidecar file (`.json`)
5. Click the `Process` button

**Returns:** A downloadable converted `.json` sidecar file.

### Convert sidecar to short

Converts all HED tags in a sidecar to short form (leaf nodes only).

**Steps:**

1. Select the `Convert to short` action
2. Toggle `Expand defs` if you want expanded definitions
3. Select the HED version
4. Upload the JSON sidecar file (`.json`)
5. Click the `Process` button

**Returns:** A downloadable converted `.json` sidecar file.

### Extract spreadsheet from sidecar

Exports sidecar content to a 4-column spreadsheet for easier editing.

**Steps:**

1. Select the `Extract HED spreadsheet` action
2. Upload the JSON sidecar file (`.json`)
3. Click the `Process` button

**Returns:** A downloadable `.tsv` spreadsheet with columns: `column_name`, `column_value`, `description`, `HED`.

See the [BIDS Annotation Quickstart](https://www.hedtags.org/hed-resources/BidsAnnotationQuickstart.html) for a tutorial on using this spreadsheet.

### Merge spreadsheet with sidecar

Imports HED annotations from a 4-column spreadsheet back into a JSON sidecar.

**Steps:**

1. Select the `Merge HED spreadsheet` action
2. Toggle `Include Description tags` to include descriptions as HED tags
3. Upload the target JSON sidecar file (`.json`)
4. Upload the spreadsheet (`.tsv` or `.xlsx`)
5. Click the `Process` button

**Returns:** A downloadable merged `.json` sidecar file.

## Working with spreadsheets

Spreadsheet tools support general-purpose HED annotation in Excel (`.xlsx`) or tab-separated (`.tsv`) format, useful when developing annotations outside of specific datasets.

### Validate a spreadsheet

Validates HED tags in spreadsheet columns.

**Steps:**

1. Select the `Validate` action
2. Toggle `Check for warnings` if you want warnings
3. Select the HED version
4. Upload a spreadsheet file (`.tsv` or `.xlsx`)
5. Select a worksheet (if Excel file with multiple sheets)
6. Check boxes next to columns containing HED tags
7. Enter prefix tags in text boxes (e.g., `Description`) if needed
8. Click the `Process` button

**Returns:** A downloadable `.txt` file of error messages if errors are found.

### Convert spreadsheet to long

Converts all HED tags in selected columns to long form.

**Steps:**

1. Select the `Convert to long` action
2. Select the HED version
3. Upload a spreadsheet file (`.tsv` or `.xlsx`)
4. Select a worksheet if needed
5. Check columns containing HED strings to convert
6. Click the `Process` button

**Returns:** A downloadable spreadsheet with converted HED tags.

### Convert spreadsheet to short

Converts all HED tags in selected columns to short form.

**Steps:**

1. Select the `Convert to short` action
2. Select the HED version
3. Upload a spreadsheet file (`.tsv` or `.xlsx`)
4. Select a worksheet if needed
5. Check columns containing HED strings to convert
6. Click the `Process` button

**Returns:** A downloadable spreadsheet with converted HED tags.

## Working with HED strings

String tools provide quick validation and conversion for individual HED annotations.

### Validate a HED string

Validates a single HED string containing tags and groups.

**Steps:**

1. Select the `Validate` action
2. Toggle `Check for warnings` if you want warnings
3. Select the HED version
4. Type or paste your HED string into the text box
5. Click the `Process` button

**Returns:** Error messages displayed in the Results box at the bottom.

### Convert string to long

Converts a HED string to long form (full paths).

**Steps:**

1. Select the `Convert to long` action
2. Select the HED version
3. Type or paste your HED string into the text box
4. Click the `Process` button

**Returns:** Converted string or error messages in the Results box.

### Convert string to short

Converts a HED string to short form (leaf nodes only).

**Steps:**

1. Select the `Convert to short` action
2. Select the HED version
3. Type or paste your HED string into the text box
4. Click the `Process` button

**Returns:** Converted string or error messages in the Results box.

## Working with HED schemas

Schema tools help HED schema developers validate, convert, and compare schemas.

View standard schemas using the [HED Schema Browser](https://www.hedtags.org/hed-schema-browser/).

### Validate a schema

Checks schema syntax and HED-3G compliance.

**Steps:**

1. Select the `Validate` action
2. Toggle `Check for warnings` if you want warnings
3. Enter a schema URL or upload a schema file (`.xml` or `.mediawiki`)
4. Click the `Process` button

**Returns:** A downloadable `.txt` file of error messages if errors are found.

### Convert a schema

Converts between `.mediawiki` and `.xml` formats.

**Steps:**

1. Select the `Convert schema` action
2. Enter a schema URL or upload a schema file (`.xml` or `.mediawiki`)
3. Click the `Process` button

**Returns:** A downloadable converted schema file.

**Note:** All HED tools use `.xml` format, but `.mediawiki` is easier to read and edit manually.

### Compare schemas

Shows differences between two schema versions.

**Steps:**

1. Select the `Compare schemas` action
2. Enter URL or upload file for first schema
3. Enter URL or upload file for second schema
4. Click the `Process` button

**Returns:** A downloadable `.txt` file with schema differences.

## Using RESTful services

HED provides REST API services for programmatic access to all tools.

### Service setup

1. Send HTTP `GET` request to obtain CSRF token: `https://hedtools.org/hed/services`
2. Extract CSRF token and cookie from response
3. Send HTTP `POST` requests with token to: `https://hedtools.org/hed/services_submit`

See [hed-matlab web services demos](https://github.com/hed-standard/hed-matlab/tree/main/hedmat/web_services_demos) for implementation examples.

### Request format

All requests are JSON dictionaries with a `service` parameter and additional parameters.

**Example:** Validating a JSON sidecar:

```json
{
    "service": "sidecar_validate",
    "schema_version": "8.4.0", 
    "json_string": "json file text",
    "check_for_warnings": "on"
}
```

### Available services

| Service                | Description                        |
| ---------------------- | ---------------------------------- |
| `get_services`         | Returns list of available services |
| `events_validate`      | Validate BIDS events file          |
| `events_assemble`      | Assemble HED annotations           |
| `events_extract`       | Extract sidecar template           |
| `sidecar_validate`     | Validate JSON sidecar              |
| `sidecar_to_long`      | Convert sidecar to long form       |
| `sidecar_to_short`     | Convert sidecar to short form      |
| `spreadsheet_validate` | Validate spreadsheet               |
| `spreadsheet_to_long`  | Convert spreadsheet to long form   |
| `spreadsheet_to_short` | Convert spreadsheet to short form  |
| `strings_validate`     | Validate HED strings               |
| `strings_to_long`      | Convert strings to long form       |
| `strings_to_short`     | Convert strings to short form      |

### Service parameters

Common parameters:

- `service` (string): Service name
- `schema_version` (string): HED version (e.g., "8.4.0")
- `schema_string` (string): Custom schema as XML string
- `check_for_warnings` (boolean): Include validation warnings
- `expand_defs` (boolean): Expand definition tags
- `events_string` (string): BIDS events file content
- `json_string` (string): JSON sidecar content
- `spreadsheet_string` (string): Spreadsheet content
- `hed_strings` (list): List of HED strings

### Service responses

All services return JSON with:

```json
{
    "service": "service_name",
    "results": {
        "command": "command_executed",
        "command_target": "data_type",
        "data": "result_or_errors",
        "schema_version": "8.4.0",
        "msg_category": "success|warning|failure",
        "msg": "explanation"
    },
    "error_type": "",
    "error_msg": ""
}
```

- Empty `error_type` and `error_msg`: Operation completed
- `msg_category`: Indicates validation result (success/warning/failure)
- `data`: Contains processed result or validation errors

## Best practices

### For annotation development

1. **Start with templates**: Generate sidecar templates from events files
2. **Use spreadsheet workflow**: Extract to spreadsheet, annotate, merge back
3. **Validate frequently**: Check annotations after each change
4. **Test with warnings**: Enable warning checks to catch potential issues early
5. **Use short form**: Shorter tags are easier to read and maintain

### For schema development

1. **Validate before converting**: Always validate schemas before format conversion
2. **Use MEDIAWIKI for editing**: Easier to read and modify than other formats
3. **Compare versions**: Use comparison tool to track changes between versions
4. **Check warnings**: Schema warnings can indicate potential issues

### For programmatic access

1. **Cache CSRF tokens**: Reuse tokens across multiple requests in a session
2. **Batch operations**: Group related operations to minimize requests
3. **Handle errors gracefully**: Check both service errors and validation results
4. **Use specific versions**: Always specify schema versions for reproducibility

## Troubleshooting

### Common validation errors

**"Invalid HED tag"**

- Tag not found in specified schema version
- Check for typos in tag names
- Verify you're using the correct schema version

**"Required tag missing"**

- Certain HED constructs require specific tags
- Check HED specification for requirements

**"Comma errors"**

- Missing or extra commas in HED string
- Tags in a group should be comma-separated
- Groups should be comma-separated

**"Placeholder errors"**

- Definition placeholders not properly filled
- Use correct syntax: `Def/MyDef/value`

### File format issues

**"Cannot parse file"**

- Ensure TSV files use tabs, not spaces
- Check for proper UTF-8 encoding
- Verify JSON files are valid JSON

**"Column not found"**

- Column names in sidecar must match events file exactly
- Column names are case-sensitive

### Schema issues

**"Cannot load schema"**

- Check internet connection for downloading standard schemas
- For custom schemas, verify XML/mediawiki format
- Ensure schema file is complete and well-formed

### Service issues

**"CSRF token error"**

- Obtain fresh token from services endpoint
- Include token in request headers
- Check that cookie is preserved across requests

**"Service timeout"**

- Large files may timeout on web interface
- Consider using Python tools for large datasets
- Break operations into smaller batches

### Getting help

- 📖 [HED Specification](https://www.hedtags.org/hed-specification)
- 💬 [GitHub Discussions](https://github.com/hed-standard/hed-specification/discussions)
- 🐛 [Report Issues](https://github.com/hed-standard/hed-web/issues)
- 📧 [Contact HED Team](mailto:hed.maintainers@gmail.com)
