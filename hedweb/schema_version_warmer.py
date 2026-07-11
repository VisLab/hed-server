"""Background warm-up for hedtools' available-HED-versions cache.

The schema-version dropdown (see ``hedweb.routes.schema_versions_results``) merges a live
GitHub listing (``hed.schema.get_available_hed_versions()``) with whatever is already known
locally. That live listing is itself cached by hedtools - a short time-based cache, then an
ETag-conditional check (see ``hed.schema.hed_cache``) - but a request that lands after that
cache has gone cold still waits, inline, on the live check before the dropdown can populate.
For ``library_name="all"`` that live check can mean dozens of serial GitHub requests, which is
what made the dropdown feel slow.

This module starts a single background thread, once, at application startup. It proactively
calls the exact same hedtools function on a fixed interval a little shorter than hedtools' own
cache window, so that cache never goes cold between refreshes. By the time any real request
needs the listing, it is almost always a fast local cache read rather than a live network call.

This is deliberately *not* a cache of hed-server's own: the warmer never stores or compares
anything itself. It only ever calls ``hed.schema.get_available_hed_versions()`` - the identical
call the route already makes - so hedtools remains the single source of truth for what is
cached and for how long.
"""

import logging
import threading

from hed import schema as hedschema

logger = logging.getLogger(__name__)

# Kept a little under hedtools' AVAILABLE_VERSIONS_TIME_THRESHOLD (60s by default) so the
# on-disk listing cache never fully expires between background refreshes.
DEFAULT_REFRESH_INTERVAL = 55

_warmer_thread = None
_stop_event = None


def _warm_loop(interval, stop_event):
    """Repeatedly refresh hedtools' available-versions cache until told to stop."""
    while not stop_event.is_set():
        try:
            # check_prerelease=True fetches the same underlying GitHub folder listings
            # (hedxml and prerelease, for every library) that check_prerelease=False needs -
            # the flag only changes how the already-fetched result is filtered afterward, not
            # what gets requested - so one warm-up call keeps both variants of the per-request
            # call served from cache.
            hedschema.get_available_hed_versions(library_name="all", check_prerelease=True)
        except Exception as ex:  # noqa: BLE001 - best-effort background refresh, never fatal
            logger.warning("Background HED available-versions cache warm-up failed: %s", ex)
        stop_event.wait(interval)


def start_warmer(interval=DEFAULT_REFRESH_INTERVAL):
    """Start the background cache-warmer thread if it is not already running.

    Parameters:
        interval (int): Seconds between warm-up calls. Should stay a little under hedtools'
            ``AVAILABLE_VERSIONS_TIME_THRESHOLD`` (60s by default) so the cache never goes
            cold between refreshes.

    Returns:
        threading.Event: The stop event for this thread (mainly useful for tests/teardown).
    """
    global _warmer_thread, _stop_event

    if _warmer_thread is not None and _warmer_thread.is_alive():
        return _stop_event

    _stop_event = threading.Event()
    _warmer_thread = threading.Thread(
        target=_warm_loop,
        args=(interval, _stop_event),
        name="hed-schema-version-warmer",
        daemon=True,
    )
    _warmer_thread.start()
    return _stop_event


def stop_warmer(timeout=5):
    """Stop the background warmer thread if one is running. Mainly for tests/teardown."""
    global _warmer_thread, _stop_event

    if _stop_event is not None:
        _stop_event.set()
    if _warmer_thread is not None:
        _warmer_thread.join(timeout=timeout)
    _warmer_thread = None
    _stop_event = None
