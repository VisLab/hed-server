"""Version information for hedweb package."""

# Version information
__version__ = "1.0.0"


def get_versions():
    """Get version information compatible with versioneer format.

    Returns:
        dict: Dictionary with 'version', 'full-revisionid', 'dirty', 'error', 'date'
    """
    return {
        "version": __version__,
        "full-revisionid": None,
        "dirty": False,
        "error": None,
        "date": None,
    }
