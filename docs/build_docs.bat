@echo off
echo Building HED Web Tools documentation with Sphinx...
sphinx-build -b html . _build/html
echo.
echo Documentation built successfully!
echo Open _build/html/index.html in your browser to view the documentation.
pause

