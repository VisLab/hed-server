# Introduction to HED web tools

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

### Key components

#### Web interface
The web interface provides an intuitive way to interact with HED data:
- **Form-based operations**: Easy-to-use forms for common HED tasks
- **File upload support**: Handle various file formats (TSV, CSV, Excel, JSON)
- **Real-time validation**: Immediate feedback on HED annotation validity
- **Download results**: Get processed files and validation reports
- 
The web interface is deployed through a Docker container and two versions are available: **hed** and **hed_dev**.

The **hed** version [https://hedtools.org/hed](https://hedtools.org/hed) relies on the released version of
the python HedTools on PyPi and the released version of the hed-web tools.

The **hed_dev** version [https://hedtools.org/hed_dev](https://hedtools.org/hed_dev) is based on the latest
version of the HedTools on GitHub and a hed-web version on a specified branch.

#### REST API
The REST API provides programmatic access to all HED operations:
- **Service endpoints**: Programmatic access to all HED operations
- **JSON communication**: Standard REST API with JSON request/response
- **Batch processing**: Handle multiple files and operations efficiently
- **Integration ready**: Easy to integrate with other tools and workflows

An example of the use the REST API can be found in the [hed-matlab](https://github.com/hed-standard/hed-matlab) repository.

### Supported operations

#### Processing tables
- **File validation**: Validate HED annotations in event and other tabular files
- **Remodeling**: Transform or summarize tabular files  using remodeling operations
- **Assembly**: Combine sidecar and event data into complete annotations
- **Search**: Find rows of a tabular file matching specific HED criteria
- **Extraction**: Extract a JSON template for HED annotations based on a tabular file.

#### Sidecar Operations
JSON files (called sidecars) contain HED annotations for BIDS datasets.
- **Validation**: Ensure sidecar files meet HED requirements
- **Extraction**: Extract a spreadsheet from a JSON file for easier annoation
- **Merging**: Merge a spreadsheet into an existing JSON file.

#### Schema Operations
HED schemas define the structure and vocabularies for HED annotations.
- **Validation**: Check HED schema files for compliance
- **Conversion**: Convert between different schema formats (XML, MediaWiki, or TSV Folder)
- **Comparison**: Compare different schema versions
- **Information**: Extract metadata and statistics from schemas

#### String Operations
HED strings are individual annotations that can be validated and processed.
The string operations are useful for quick checks.
- **Validation**: Validate individual HED annotation strings
- **Assembly**: Combine HED strings with proper syntax
- **Conversion**: Convert between different HED string formats
- **Search**: Find specific tags or patterns in HED strings

#### Spreadsheet Processing
Spreadsheets provide a convenient way to manage HED annotations in tabular format.
- **Column mapping**: Map spreadsheet columns to HED concepts
- **Validation**: Validate HED data in spreadsheet format
- **Conversion**: Convert between spreadsheet and other formats

## Architecture

The HED Web Tools are organized into several key modules:

- **App Factory** (`app_factory.py`): Flask application configuration and setup
- **Routes** (`routes.py`): Web interface endpoints and request handling
- **Process forms** (`process_forms.py`): Handles form submissions and file uploads
- **Process Service** (`process_service.py`): Core processing logic for service coordination
- **Operations Modules**: Specialized modules for different types of HED operations
- **Web Utilities** (`web_util.py`): Common utilities for web operations

## Getting Started

To get started with HED Web Tools:

1. **Installation**: Follow the installation instructions in the main documentation
2. **Basic Usage**: Try the web interface at `http://localhost:5000`
3. **API Access**: Use the REST endpoints for programmatic access
4. **Examples**: Check the user guide for step-by-step examples
