import argparse
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import logging
import zipfile

# Set up basic logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

def unzip_sbom(zip_file, extract_to):
    """
    Unzips the SBOM zip file to the specified directory.
    """
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        return True
    except zipfile.BadZipFile:
        logging.error(f"Invalid zip file: {zip_file}")
        return False
    except Exception as e:
        logging.error(f"Error unzipping file {zip_file}: {e}")
        return False

def run_merge(files_to_merge, output_file):
    # ... [previous run_merge function] ...

def split_into_chunks(lst, n):
    # ... [previous split_into_chunks function] ...

def main(zip_path, chunk_size, num_threads):
    # Unzip the SBOM zip file
    extract_to = os.path.splitext(zip_path)[0]
    if not unzip_sbom(zip_path, extract_to):
        return False

    # ... [rest of the main function with dir_path replaced by extract_to] ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge SBOM XML files from a zip file using CycloneDX.")
    parser.add_argument('--zipfile', '-z', help="Path to the SBOM zip file.")
    parser.add_argument('--chunk-size', type=int, default=5, help="Number of files to process in each batch.")
    parser.add_argument('--threads', type=int, default=4, help="Number of parallel threads to use.")

    args = parser.parse_args()

    if args.zipfile:
        zip_path = args.zipfile
    else:
        zip_path = input("Enter the path to the SBOM zip file: ")

    if not os.path.isfile(zip_path):
        logging.error(f"The file {zip_path} does not exist.")
    else:
        if not main(zip_path, args.chunk_size, args.threads):
            logging.error("The merging process encountered errors.")
