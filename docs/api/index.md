# API Reference Overview

The HED Web Tools API provides a comprehensive set of modules for processing Hierarchical Event Descriptor (HED) data through web interfaces and programmatic access. The API is designed around a service-oriented architecture with clear separation of concerns.

## Architecture Overview

```
Web Interface ──┐
                ├─► Flask Routes ──┬─► StringOperations
Client ─► REST API ──┘              ├─► EventOperations
                                    ├─► SchemaOperations
                                    ├─► SidecarOperations
                                    └─► SpreadsheetOperations
```

---

## Module Structure

### 1. Application Layer
- **[App Factory](app_factory.md)** - Flask application configuration and initialization
- **[Routes](routes.md)** - Web interface endpoints and HTTP request handling

### 2. Service Layer  
- **[Process Service](process_service.md)** - Core orchestration and business logic
- **[Process Form](process_form.md)** - Form data extraction and validation
- **[Base Operations](base_operations.md)** - Common base classes and shared functionality

### 3. Operation Modules
- **[Event Operations](event_operations.md)** - Process event files with HED annotations
- **[Schema Operations](schema_operations.md)** - Validate and manipulate HED schemas
- **[Sidecar Operations](sidecar_operations.md)** - Handle BIDS sidecar JSON files
- **[Spreadsheet Operations](spreadsheet_operations.md)** - Process tabular data with HED columns
- **[String Operations](string_operations.md)** - Validate and manipulate HED strings

### 4. Utility Modules
- **[Columns](columns.md)** - Column mapping and data structure utilities
- **[Web Utils](web_util.md)** - Common web application helper functions

---

## Service Categories

### HED Schema Services
Handle HED schema files and validation:
- Schema validation and compliance checking
- Format conversion (XML ↔ MediaWiki)
- Schema comparison and analysis
- Version management

### HED String Services  
Process individual HED annotation strings:
- Syntax validation and error reporting
- Format conversion (short ↔ long form)
- String assembly and validation
- Placeholder resolution

### HED Event Services
Work with event data files:
- Event file validation against HED schemas
- HED annotation assembly from spreadsheets
- Event file format conversion
- Batch processing capabilities

### HED Sidecar Services
Handle BIDS-compliant sidecar files:
- JSON sidecar validation
- HED annotation extraction and validation
- Sidecar format conversion
- Integration with BIDS datasets

### HED Spreadsheet Services
Process tabular data with HED annotations:
- Excel and CSV file processing
- Column mapping and validation
- HED string assembly from columns
- Data export and format conversion

---

## Getting Started

```{tip}
New to the API? Start with the [Getting Started Guide](getting_started.md) for a quick introduction.
```

### Quick Example

```python
from hedweb import create_app
from hedweb.string_operations import StringOperations

# Initialize the application
app = create_app()

# Create string operations service
string_ops = StringOperations()

# Validate a HED string
result = string_ops.process_string_data({
    'hed_string': 'Sensory-event, Visual-presentation',
    'schema_version': '8.2.0',
    'command': 'validate'
})

print(result['data'])  # Validation results
```

---

## API Reference

```{toctree}
:maxdepth: 2

getting_started
architecture
service_categories
api_usage
app_factory
routes
base_operations
process_form
process_service
columns
web_util
event_operations
schema_operations
sidecar_operations
spreadsheet_operations
string_operations
```

## External References

- **[HED Standard](https://www.hedtags.org/)** - Official HED specification
- **[BIDS Standard](https://bids.neuroimaging.io/)** - Brain Imaging Data Structure
- **[Flask Documentation](https://flask.palletsprojects.com/)** - Web framework documentation
