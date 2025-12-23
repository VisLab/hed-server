# Introduction

## What is HED?

HED (Hierarchical Event Descriptors) is a standardized vocabulary and annotation framework designed to systematically describe events in experimental data, particularly neuroimaging and behavioral data. HED tags are comma-separated path strings that describe what happened, when it happened, and other relevant properties of experimental events as well as other experimental metadata.

For example, a HED annotation describing the display of a face image might look like:

```hed
Sensory-event, Visual-presentation, (Image, Face)
```

HED is integrated into major neuroimaging standards:

* [BIDS](https://bids.neuroimaging.io/) (Brain Imaging Data Structure)
* [NWB](https://www.nwb.org/) (Neurodata Without Borders)

## What are HED web tools?

HED web tools provide both a web-based interface and REST API services for working with HED annotations and schemas. The application is built using Flask and offers easy access to HED operations without requiring programming knowledge.

### Web interface

The browser-based interface provides:

- **Form-based operations**: Easy-to-use forms for common HED tasks
- **File upload support**: Handle various file formats (TSV, CSV, Excel, JSON)
- **Real-time validation**: Immediate feedback on HED annotation validity
- **Download results**: Get processed files and validation reports
- **No login required**: Free to use for everyone

Two deployments are available:

- **Production** ([hedtools.org/hed](https://hedtools.org/hed)): Stable release based on PyPI packages
- **Development** ([hedtools.org/hed_dev](https://hedtools.org/hed_dev)): Latest features from GitHub

### REST API

The REST API provides programmatic access to the operations:

- **Service endpoints**: Full access to HED operations
- **JSON communication**: Standard REST API with JSON request/response format
- **Batch processing**: Handle multiple files and operations efficiently
- **Integration ready**: Easy to integrate with other tools and workflows

Example implementations are available in the [hed-matlab](https://github.com/hed-standard/hed-matlab) repository.

## Key features

### Processing tabular files (TSV)

- **Validation**: Validate HED annotations in tabular files, with and without JSON metadata
- **Assembly**: Combine JSON sidecar and tabular data into complete annotations
- **Search**: Find rows matching specific HED criteria
- **Template generation**: Create JSON sidecar templates from tabular files
- **Remodeling**: Transform or summarize tabular data using remodeling operations

### Sidecar operations (JSON)

- **Validation**: Ensure sidecar files meet HED requirements
- **Conversion**: Convert between short and long tag forms
- **Spreadsheet extraction**: Export to 4-column spread sheet for easier editing
- **Spreadsheet merging**: Import annotations from spreadsheets back to JSON

JSON sidecars contain HED annotations and metadata for BIDS datasets.

### Spreadsheet processing

- **Column validation**: Validate HED data in specific spreadsheet columns
- **Format conversion**: Convert between short and long tag forms
- **Flexible formats**: Support for both TSV and Excel I/O

Spreadsheets provide a convenient way to develop HED annotations outside of specific datasets.

### String operations

- **Quick validation**: Validate individual HED strings
- **Format conversion**: Convert between short and long forms
- **Interactive testing**: Test annotations during development

String operations are useful for quick checks and learning HED syntax.

### Schema operations

- **Schema validation**: Check HED schema files for compliance
- **Format conversion**: Convert between XML, MEDIAWIKI, and TSV formats
- **Schema comparison**: Compare different schema versions
- **Metadata extraction**: Extract information and statistics from schemas

HED schemas define the structure and vocabularies for HED annotations.

## Use cases

### For researchers

- Validate HED annotations during BIDS or NWB dataset preparation
- Convert between tag formats for better readability
- Generate sidecar templates to streamline annotation
- Test annotations interactively during development

### For annotators

- Use spreadsheet workflow for easier editing
- Validate annotations frequently to catch errors early
- Use short tag form not full paths
- Access tools without installing software

### For developers

- Integrate HED validation into data processing pipelines
- Batch process multiple files programmatically
- Validate annotations as part of CI/CD workflows
- Build custom tools on top of HED services

### For schema developers

- Validate schema syntax and compliance
- Convert between formats for different purposes
- Compare schema versions to track changes
- Test schema modifications before release

## Getting started

Ready to start using HED web tools? Check out:

- [User guide](user_guide.md) - Comprehensive guide to all features
- [Installation](installation.md) - Deploy your own instance
- [API reference](api/index.rst) - Developer documentation
- [HED resources](https://www.hedtags.org/hed-resources) - Additional learning materials
