#!/usr/bin/env python
import os
import sys
from http.server import SimpleHTTPRequestHandler, test


class MockServer:
    @staticmethod
    def run(directory=None):
        SimpleHTTPRequestHandler.extensions_map = {
            k: f"{v};charset=UTF-8"
            for k, v in SimpleHTTPRequestHandler.extensions_map.items()
        }
        if directory is None:
            directory = sys.argv[1] if len(sys.argv) > 1 else "html"
        os.chdir(directory)
        test(SimpleHTTPRequestHandler)


if __name__ == "__main__":
    MockServer.run()
