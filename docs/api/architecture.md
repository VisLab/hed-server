# Architecture Overview

```mermaid
graph TD
    A[Web Interface] --> C{Flask Routes}
    B[Client] --> D[REST API] --> C

    C --> E[StringOperations]
    C --> F[EventOperations]
    C --> G[SchemaOperations]
    C --> H[SidecarOperations]
    C --> I[SpreadsheetOperations]
```

The HED Web Tools API is designed around a service-oriented architecture with clear separation of concerns.

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
