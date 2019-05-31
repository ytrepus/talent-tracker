#!/usr/bin/env bash
flask db upgrade
python scripts/seed-staging.py