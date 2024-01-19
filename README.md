# merge_sbom

[![GitHub license](https://img.shields.io/github/license/ReFirmLabs/binwalk.svg)](LICENSE)

# SBOM Merge Script

## Description

This script is designed to merge a large number of SBOM (Software Bill of Materials) files using the CycloneDX CLI tool. It utilizes parallel processing to handle multiple files simultaneously, enhancing efficiency. The script also provides a progress bar for visual feedback and includes logging for error tracking.

## Requirements

- Python 3.x
- CycloneDX CLI tool installed and accessible in the system path

## Installation

1. Clone this repository or download the script to your local machine.

    ```bash
    git clone https://github.com/davidmthomsen/merge_sbom.git
    cd merge_sbom
    ```

2. Install the required Python dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

You can run the script with command-line arguments or interactively:

- To run with arguments:

    ```bash
    python3 merge_sbom.py --directory /path/to/your/sbom/directory --chunk-size 5 --threads 4
    ```

- To run interactively, simply execute the script and enter the required information when prompted:

    ```bash
    python3 merge_sbom.py
    ```

### Arguments

- `--directory` or `-d`: Specify the directory containing SBOM XML files.
- `--chunk-size`: Number of files to process in each batch (default is 5).
- `--threads`: Number of parallel threads to use (default is 4).

## Features

- Parallel processing of SBOM files.
- Progress bar to monitor the merge process.
- Logging to track errors and important information.
- Flexibility to run with command-line arguments or interactively.

## Contributing

Contributions to this script are welcome. Please fork the repository and submit a pull request with your changes.

---

