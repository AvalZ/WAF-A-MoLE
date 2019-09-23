#!/bin/sh
sphinx-apidoc -f -o docs/source wafamole && cd docs && make html