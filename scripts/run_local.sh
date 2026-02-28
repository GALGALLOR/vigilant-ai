#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /path/to/video.mp4"
  exit 1
fi

modal run workers/inference.py::run_pipeline --input-video "$1"
