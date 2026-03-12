# HED web scratch history

## Purpose

Document failed attempts, dead ends, and lessons learned to prevent repeating mistakes.

## Failed attempts log

<!-- Record what was tried, why it failed, and what worked instead. Example:
### Attempt: returning hedtools exceptions directly in JSON responses
**Date:** 2025-xx-xx
**Issue:** Internal stack traces leaked to API consumers; unhelpful error messages
**Solution:** Catch hedtools exceptions in *_operations.py and return structured JSON with a user-friendly message and HTTP 400/422
-->

## Common pitfalls

<!-- Document recurring issues and how to avoid them. Example:
### Pitfall: CSRF token missing in AJAX requests
**Symptoms:** Flask-WTF returns 400 Bad Request for POST requests made via JavaScript fetch/axios
**Fix:** Include the CSRF token as a request header (`X-CSRFToken`) fetched from the meta tag in the page template
-->
