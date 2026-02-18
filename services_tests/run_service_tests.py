#!/usr/bin/env python
"""
Script to run service tests locally by starting the HED web server and running tests against it.

This script:
1. Starts the HED web server on a configurable port (default: 5000)
2. Waits for the server to be ready
3. Runs the service tests
4. Shuts down the server when tests complete

Usage:
    python services_tests/run_service_tests.py [--port PORT] [--timeout TIMEOUT]

Options:
    --port PORT         Port to run the server on (default: 5000)
    --timeout TIMEOUT   Timeout in seconds to wait for server (default: 30)
    --verbose          Show server output
"""

import argparse
import multiprocessing
import os
import sys
import time
import unittest
from contextlib import contextmanager

import requests


def run_server(port, verbose):
    """Run the HED web server in a separate process."""
    # Suppress server output unless verbose mode is enabled
    if not verbose:
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")

    from hedweb.runserver import create_app_with_routes

    app = create_app_with_routes()
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


def wait_for_server(url, timeout=30):
    """Wait for the server to be ready."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except (requests.ConnectionError, requests.Timeout):
            time.sleep(0.5)
    return False


@contextmanager
def hed_server(port, verbose=False):
    """Context manager to start and stop the HED server."""
    # Start server process
    server_process = multiprocessing.Process(
        target=run_server, args=(port, verbose), daemon=True
    )
    server_process.start()

    # Wait for server to be ready
    server_url = f"http://127.0.0.1:{port}"
    print(f"Starting HED web server on {server_url}...")

    if not wait_for_server(server_url, timeout=30):
        server_process.terminate()
        server_process.join(timeout=5)
        raise RuntimeError(f"Server failed to start within 30 seconds on {server_url}")

    print(f"Server is ready at {server_url}")

    try:
        yield server_url
    finally:
        print("\nShutting down server...")
        server_process.terminate()
        server_process.join(timeout=5)
        if server_process.is_alive():
            server_process.kill()
            server_process.join()


def run_tests(server_url):
    """Run the service tests."""
    # Set environment variable for tests to use
    os.environ["HED_SERVER_URL_KEY"] = server_url

    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover("services_tests", pattern="test*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def main():
    parser = argparse.ArgumentParser(
        description="Run HED service tests with a local test server"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to run the test server on (default: 5000)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in seconds to wait for server startup (default: 30)",
    )
    parser.add_argument("--verbose", action="store_true", help="Show server output")

    args = parser.parse_args()

    try:
        with hed_server(args.port, args.verbose) as server_url:
            success = run_tests(server_url)
            sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Required for Windows multiprocessing
    multiprocessing.freeze_support()
    main()
