# HED online tools

![Python3](https://img.shields.io/badge/python-%3E=3.10-blue.svg) [![Documentation](https://img.shields.io/badge/docs-hedtags.org-blue.svg)](https://www.hedtags.org/hed-web) [![Maintainability](https://qlty.sh/gh/hed-standard/projects/hed-web/maintainability.svg)](https://qlty.sh/gh/hed-standard/projects/hed-web) [![Code Coverage](https://qlty.sh/gh/hed-standard/projects/hed-web/coverage.svg)](https://qlty.sh/gh/hed-standard/projects/hed-web)

## What is HED?

HED (Hierarchical Event Descriptors) is a framework for systematically describing both laboratory and real-world events. HED tags are comma-separated path strings. The goal of HED is to describe precisely the nature of the events of interest occurring in an experiment using a common structured vocabulary and standardized tools. The HED framework has been developed for neurological imaging data (e.g., EEG, MEG, iEEG, fMRI), physiological (e.g., ECG, EMG, GSR) as well as multimodal experiment (e.g., mobile brain/body imaging). HED has been adopted as part of the BIDS ([**https://bids.neuroimaging.io**](https://bids.neuroimaging.io)) standard for brain imaging and accepted as a standard by the INCF ([**https://www.incf.org**](https://www.incf.org)).

## HED online tools

The HED online tools are a set of web-based applications for validating and analyzing Hierarchical Event Descriptors (HED) annotations. These tools rely on are designed to be used in a web browser and can be deployed locally or from a DOCKER container.

| Resource              | URL                                                                                | Description                            |
| --------------------- | ---------------------------------------------------------------------------------- | -------------------------------------- |
| **HED Tools (PyPI)**  | [https://hedtools.org/hed](https://hedtools.org/hed)                               | Production version of HED online tools |
| **HED Tools (main)**  | [https://hedtools.org/hed_dev](https://hedtools.org/hed_dev)                       | Latest features, some experimental     |
| **HED Resources**     | [https://www.hedtags.org/hed-resources](https://www.hedtags.org/hed-resources)     | Documentation and tutorials            |
| **API Documentation** | [https://www.hedtags.org/hed-web](https://www.hedtags.org/hed-web)                 | Technical documentation                |
| **GitHub Repository** | [https://github.com/hed-standard/hed-web](https://github.com/hed-standard/hed-web) | Source code and issues                 |

### User Guide

- Quick start, local run, Docker deployment, and reverse proxy setup: see [docs/user_guide.md](docs/user_guide.md).
- Deployment script now supports an optional third parameter to bind host ports (e.g., `127.0.0.1` for localhost-only): `./deploy.sh [branch] [environment] [bind_address]`.

### HED Tools Online

## 

#### HED online tools summary

The following table summarizes the available online tools. The tools are organized around the types of data that the tools handle. The Actions refer to the types of actions that can be performed on the data through the online tools. Each action is linked to its corresponding documentation to provide additional information. **NEW: an experimental [CTagger](http://ctagger.hed.tools) online annotation tool is now available**.

| Data type        | Action                                                                                                                | Description                                                                                                        |
| ---------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Events**       | [Validate](https://www.hedtags.org/hed-resources/HedOnlineTools.html#validate-an-events-file)                         | Validate HED in a tabular file and its sidecar.                                                                    |
|                  | [Assemble HED annotations](https://www.hedtags.org/hed-resources/HedOnlineTools.html#assemble-annotations)            | Return a list of the assembled HED strings for a tabular file.                                                     |
|                  | [Search HED strings](https://www.hedtags.org/hed-resources/HedOnlineTools.html#search-annotations)                    | Return a vector of 0's and 1's based on a HED search query of HED annotation strings extracted from an event file. |
|                  | [Generate JSON sidecar template](https://www.hedtags.org/hed-resources/HedOnlineTools.html#generate-sidecar-template) | Create a sidecar template from a tabular file.                                                                     |
|                  | [Execute remodel script](https://www.hedtags.org/hed-resources/HedOnlineTools.html#execute-remodel-script)            | Execute JSON script of [HED remodeling commands](https://www.hedtags.org/hed-resources/FileRemodelingTools.html).  |
| **Sidecars**     | [Validate](https://www.hedtags.org/hed-resources/HedOnlineTools.html#validate-a-sidecar)                              | Validate HED in a BIDS JSON sidecar.                                                                               |
|                  | [Convert to long](https://www.hedtags.org/hed-resources/HedOnlineTools.html#convert-sidecar-to-long)                  | Convert HED tags in a sidecar to full paths.                                                                       |
|                  | [Convert to short](https://www.hedtags.org/hed-resources/HedOnlineTools.html#convert-sidecar-to-short)                | Convert HED tags in a sidecar to single tags.                                                                      |
|                  | [Extract HED spreadsheet](https://www.hedtags.org/hed-resources/HedOnlineTools.html#extract-spreadsheet-from-sidecar) | Create a 4-column spreadsheet from HED in a sidecar.                                                               |
|                  | [Merge HED spreadsheet](https://www.hedtags.org/hed-resources/HedOnlineTools.html#merge-a-spreadsheet-with-a-sidecar) | Merge HED from spreadsheet into a JSON sidecar.                                                                    |
| **Spreadsheets** | [Validate](https://www.hedtags.org/hed-resources/HedOnlineTools.html#validate-a-spreadsheet)                          | Validate HED in a spreadsheet (.xlsx or .tsv).                                                                     |
|                  | [Convert to long](https://www.hedtags.org/hed-resources/HedOnlineTools.html#convert-spreadsheet-to-long)              | Convert HED tags in a spreadsheet to full paths.                                                                   |
|                  | [Convert to short](https://www.hedtags.org/hed-resources/HedOnlineTools.html#convert-spreadsheet-to-short)            | Convert HED tags in a spreadsheet to single tags.                                                                  |
| **Strings**      | [Validate](https://www.hedtags.org/hed-resources/HedOnlineTools.html#validate-a-hed-string)                           | Validate a HED string.                                                                                             |
|                  | [Convert to long](https://www.hedtags.org/hed-resources/HedOnlineTools.html#convert-a-hed-string-to-long)             | Convert a HED string to full paths.                                                                                |
|                  | [Convert to short](https://www.hedtags.org/hed-resources/HedOnlineTools.html#convert-a-hed-string-to-short)           | Convert a HED string to single tags.                                                                               |
|                  | [Search HED strings](https://www.hedtags.org/hed-resources/HedOnlineTools.html#search-a-hed-string)                   | Search a HED string based on a HED search query.                                                                   |
| **Schemas**      | [Validate](https://www.hedtags.org/hed-resources/HedOnlineTools.html#validate-a-hed-schema)                           | Validate a HED schema.                                                                                             |
|                  | [Convert schema](https://www.hedtags.org/hed-resources/HedOnlineTools.html#convert-a-hed-schema)                      | Convert a HED schema to other format.                                                                              |
|                  | [Compare HED schemas](https://www.hedtags.org/hed-resources/HedOnlineTools.html#compare-hed-schemas)                  | Show differences between two HED schemas.                                                                          |

**Events files** are tabular (tab-separated) files. The first row of an events file contains column names. Each subsequent row corresponds to an event marker at a specified time in the corresponding data file.

**Note:** The operations listed for events file apply to any tabular (tab-separated value) file with column names.

**Sidecars** are JSON text files containing metadata. Sidecars follow the requirements of the [BIDS (Brain Imaging Data Structure)](https://bids-specification.readthedocs.io/en/stable/) standard.

**Spreadsheets** contain tabular data in either as an Excel (`.xlsx`) or as a tab-separated (`.tsv`) text file. They are used for convenience in assigning HED tags to event codes.

**Strings** refer to HED annotations, which are entered as strings for quick checks for validity or conversion.

**Schemas** refer to HED schema vocabularies, which may be either in .mediawiki or .xml format. These tools are used by schema developers creating the HED vocabularies and are not of interest to annotators or analysts.

More detailed help on using these online tools is available in the HED online tools [**User guide**](https://www.hedtags.org/hed-resources/HedOnlineTools.html#).

#### HED REST services

The HED online tools are also available as callable web services. More detailed help on calling these services is available at: [**HED RESTful services**](https://www.hedtags.org/hed-resources/HedOnlineTools.html#hed-restful-services) Downloadable examples of calling these services from a MATLAB program can be found in the GitHub MATLAB [**Web service demos**](https://github.com/hed-standard/hed-matlab/tree/main/hedmat/web_services_demos).

#### Where to find out more?

- The [**HED home page**](https://www.hedtags.org) has links to all things HED.
- The [**HED GitHub organization**](https://github.com/hed-standard) contains the source for code and docs for HED.
- The [**HED schema viewer**](https://www.hedtags.org/hed-schema-browser) allows you to browse HED vocabularies, both released and under development.
- The [**HED resources**](https://www.hedtags.org/hed-resources) has links to all HED documentation.

### Online deployment

The stable version of the HED online tools is available for your use at: [**https://hedtools.org/hed**](https://hedtools.org/hed). An alternate version [**https://hedtools.org/hed_dev**](https://hedtools.org/hed_dev) has the latest features, some of which are experimental.

## Testing

### Unit Tests

Run the main test suite without requiring external services:

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run all unit tests
python -m unittest discover -s tests -p "test*.py" -v
```

### Service Tests (Integration Tests)

Service tests validate the REST API endpoints by making HTTP requests to a running HED web server.

**Option 1: Automatic (Recommended)**\
Use the provided script that starts the server, runs tests, and cleans up automatically:

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run service tests with automatic server management
python run_service_tests.py
```

**Option 2: VS Code Task**\
Use the integrated task runner:

1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select "Run Service Tests (with local server)"

**Option 3: Manual Server Management**\
Start the server in one terminal and run tests in another:

Terminal 1 - Start server:

```powershell
.\.venv\Scripts\Activate.ps1
python hedweb/runserver.py
```

Terminal 2 - Run tests:

```powershell
.\.venv\Scripts\Activate.ps1
python -m unittest discover services_tests
```

For more details, see [.status/running-service-tests-locally.md](.status/running-service-tests-locally.md).
