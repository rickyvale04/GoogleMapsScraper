#!/usr/bin/env python3
"""Backward-compatible entry point. Use api/server.py directly for new code."""

from api.server import app, run_server

if __name__ == '__main__':
    run_server()
