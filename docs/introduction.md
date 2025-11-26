# Introduction

## What is HED?

HED (Hierarchical Event Descriptor) is a system for describing events in machine-actionable form.
HED tags are comma-separated path strings that describe what happened, when it happened,
and other relevant properties of experimental events.

For example, a HED annotation might look like:
```
Sensory-event, Visual-presentation, (Image, Face)
```

## HED web tools overview

HED Web Tools provides a web-based interface for working with HED annotations and schemas.
The application is built using Flask and offers both a user-friendly web interface
and REST API endpoints for programmatic access.

### Web interface

- **Form-based operations**: Easy-to-use forms for common HED tasks.
- **File upload support**: Handle various file formats (TSV, CSV, Excel, JSON).
- **Real-time validation**: Immediate feedback on HED annotation validity.
- **Download results**: Get processed files and validation reports.

The web interface provides an intuitive way to interact with HED data.
The interface is deployed through a Docker container and two versions are available: 
**hed** and **hed_dev**.

The **hed** version [https://hedtools.org/hed](https://hedtools.org/hed) relies on the released version of
the python HedTools on PyPi and the released version of the hed-web tools.

The **hed_dev** version [https://hedtools.org/hed_dev](https://hedtools.org/hed_dev) is based on the latest
version of the HedTools on GitHub and a hed-web version on a specified branch.

### REST API

- **Service endpoints**: Programmatic access to all HED operations.
- **JSON communication**: Standard REST API with JSON request/response.  
- **Batch processing**: Handle multiple files and operations efficiently.
- **Integration ready**: Easy to integrate with other tools and workflows.

The REST API provides programmatic access to all HED operations.
An example of the use the REST API can be found in the 
[hed-matlab](https://github.com/hed-standard/hed-matlab) repository.

## Supported operations

### Processing tables

- **File validation**: Validate HED annotations in event and other tabular files.
- **Remodeling**: Transform or summarize tabular files  using remodeling operations.
- **Assembly**: Combine sidecar and event data into complete annotations.
- **Search**: Find rows of a tabular file matching specific HED criteria.
- **Extraction**: Extract a JSON template for HED annotations based on a tabular file.

### Sidecar operations

- **Validation**: Ensure sidecar files meet HED requirements.
- **Extraction**: Extract a spreadsheet from a JSON file for easier annotation.
- **Merging**: Merge a spreadsheet into an existing JSON file.  

JSON files (called sidecars) contain HED annotations for BIDS datasets.  

### Schema operations

- **Validation**: Check HED schema files for compliance.
- **Conversion**: Convert between different schema formats (XML, MediaWiki, or TSV Folder).
- **Comparison**: Compare different schema versions.
- **Information**: Extract metadata and statistics from schemas.

HED schemas define the structure and vocabularies for HED annotations.  

### String operations

- **Validation**: Validate individual HED annotation strings.
- **Assembly**: Combine HED strings with proper syntax.
- **Conversion**: Convert between different HED string formats.
- **Search**: Find specific tags or patterns in HED strings.

HED strings are individual annotations that can be validated and processed.
The string operations are useful for quick checks.  

### Spreadsheet processing

- **Column mapping**: Map spreadsheet columns to HED concepts.
- **Validation**: Validate HED data in spreadsheet format.
- **Conversion**: Convert between spreadsheet and other formats.

Spreadsheets provide a convenient way to manage HED annotations in tabular format. 