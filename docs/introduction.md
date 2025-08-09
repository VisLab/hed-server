# Introduction to HED Web Tools

## What is HED?

HED (Hierarchical Event Descriptor) is a system for describing events in machine-actionable form. HED tags are comma-separated path strings that describe what happened, when it happened, and other relevant properties of experimental events.

For example, a HED annotation might look like:
```
Sensory-event, Visual-presentation, (Image, Face), (Onset, Delay/2.3 s)
```

## HED Web Tools Overview

HED Web Tools provides a web-based interface for working with HED annotations and schemas. The application is built using Flask and offers both a user-friendly web interface and REST API endpoints for programmatic access.

### Key Components

#### Web Interface
- **Form-based operations**: Easy-to-use forms for common HED tasks
- **File upload support**: Handle various file formats (TSV, CSV, Excel, JSON)
- **Real-time validation**: Immediate feedback on HED annotation validity
- **Download results**: Get processed files and validation reports

#### REST API
- **Service endpoints**: Programmatic access to all HED operations
- **JSON communication**: Standard REST API with JSON request/response
- **Batch processing**: Handle multiple files and operations efficiently
- **Integration ready**: Easy to integrate with other tools and workflows

### Supported Operations

#### Schema Operations
- **Validation**: Check HED schema files for compliance
- **Conversion**: Convert between different schema formats
- **Comparison**: Compare different schema versions
- **Information**: Extract metadata and statistics from schemas

#### String Operations
- **Validation**: Validate individual HED annotation strings
- **Assembly**: Combine HED strings with proper syntax
- **Conversion**: Convert between different HED string formats
- **Search**: Find specific tags or patterns in HED strings

#### Event Processing
- **File validation**: Validate HED annotations in event files
- **Remodeling**: Transform event structures using remodeling operations
- **Assembly**: Combine sidecar and event data into complete annotations
- **Search**: Find events matching specific HED criteria

#### Sidecar Operations
- **BIDS support**: Work with BIDS sidecar JSON files
- **Validation**: Ensure sidecar files meet HED requirements
- **Extraction**: Extract HED-related information from sidecars
- **Merging**: Combine multiple sidecar files

#### Spreadsheet Processing
- **Column mapping**: Map spreadsheet columns to HED concepts
- **Validation**: Validate HED data in spreadsheet format
- **Conversion**: Convert between spreadsheet and other formats
- **Batch processing**: Handle multiple spreadsheets simultaneously

## Architecture

The HED Web Tools are organized into several key modules:

- **App Factory** (`app_factory.py`): Flask application configuration and setup
- **Routes** (`routes.py`): Web interface endpoints and request handling
- **Process Service** (`process_service.py`): Core processing logic and service coordination
- **Operations Modules**: Specialized modules for different types of HED operations
- **Web Utilities** (`web_util.py`): Common utilities for web operations

## Getting Started

To get started with HED Web Tools:

1. **Installation**: Follow the installation instructions in the main documentation
2. **Basic Usage**: Try the web interface at `http://localhost:5000`
3. **API Access**: Use the REST endpoints for programmatic access
4. **Examples**: Check the user guide for step-by-step examples
