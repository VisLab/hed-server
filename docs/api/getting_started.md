# Getting Started Guide

## Quick Start

1. **Choose your service** based on the type of HED data you're processing
2. **Check the specific module documentation** for detailed parameter information
3. **Use the web interface** for interactive processing
4. **Access REST endpoints** for programmatic integration

## Integration Examples

### Python Integration
```python
import requests

response = requests.post('http://localhost:5000/services/strings', json={
    "service": "strings_validate",
    "schema_version": "8.3.0", 
    "hed_strings": ["Sensory-event, Visual-presentation"]
})
```

### MATLAB Integration

See the web services examples in the [hed-matlab](https://github.com/hed-standard/hed-matlab)
GitHub repository for detailed examples of calling these services from MATLAB.

### Web Interface
Navigate to the appropriate section (Strings, Events, etc.) and use the form-based interface 
for interactive processing.

For detailed information about each module's functions, classes, and parameters, 
see the individual module documentation pages.
