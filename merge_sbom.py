import argparse
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures import TimeoutError
from tqdm import tqdm
import logging
import zipfile

# Set up basic logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.ERROR)

def unzip_sbom(zip_file, extract_to):
    """
    Unzips the SBOM zip file to the specified directory.
    """
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        logging.info(f"Unzipped {zip_file} to {extract_to}")
        return True
    except zipfile.BadZipFile:
        logging.error(f"Invalid zip file: {zip_file}")
        return False
    except Exception as e:
        logging.error(f"Error unzipping file {zip_file}: {e}")
        return False

def run_merge(files_to_merge, output_file):
    """
    Executes the CycloneDX merge command for a list of files.
    """
    try:
        subprocess.run(['cyclonedx', 'merge', '--input-files'] + files_to_merge + ['--output-file', output_file], check=True, stdout=subprocess.DEVNULL)
        # logging.info(f"Merged files into {output_file}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error in merging files into {output_file}: {e}")
        return False
    return True

def split_into_chunks(lst, n):
    """
    Splits a list into chunks of size n.
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def main(zip_path, chunk_size, num_threads):
    """
    Main function to merge SBOM files from a zip file.
    """
    # Determines the extraction directory based on the zip file name
    extract_to = os.path.splitext(zip_path)[0]
    if not unzip_sbom(zip_path, extract_to):
        return False
    
    # Lists all XML files in the extracted directory
    files = [os.path.join(extract_to, f) for f in os.listdir(extract_to) if f.endswith('.xml')]
    # Splits files into manageable chunks
    file_chunks = list(split_into_chunks(files, chunk_size))
    # Generates names for intermediate merged files
    intermediate_files = [f"intermediate_{i}.xml" for i in range(len(file_chunks))]

    success = True
    # Using ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Submits merge tasks for each chunk
        future_to_chunk = {executor.submit(run_merge, chunk, os.path.join(extract_to, intermediate)): chunk for chunk, intermediate in zip(file_chunks, intermediate_files)}

        # Progress bar to monitor the process
        with tqdm(total=len(future_to_chunk), desc="Merging Files", unit="chunk") as progress:
            for future in as_completed(future_to_chunk, timeout=120):
                try:
                # Checks for errors in completed futures
                    if not future.result():
                        success = False
                except TimeoutError:
                    logging.error("Processing timed out for a chunk")
                    success = False
                progress.update(1)

    # Merging the intermediate files into the final output
    if success:
        final_output = os.path.join(extract_to, "final_merged.xml")
        # Filters out non-existing intermediate files before final merge
        existing_intermediates = [os.path.join(extract_to, f) for f in intermediate_files if os.path.exists(os.path.join(extract_to, f))]
        if not run_merge(existing_intermediates, final_output):
            success = False

    return success

if __name__ == "__main__":
    # Command-line interface setup
    parser = argparse.ArgumentParser(description="Merge SBOM XML files from a zip file using CycloneDX.")
    parser.add_argument('--zipfile', '-z', help="Path to the SBOM zip file.")
    parser.add_argument('--chunk-size', type=int, default=5, help="Number of files to process in each batch.")
    parser.add_argument('--threads', type=int, default=4, help="Number of parallel threads to use.")

    args = parser.parse_args()

    # Getting the zip file path from arguments or user input
    zip_path = args.zipfile or input("Enter the path to the SBOM zip file: ")

    # Checks if the zip file exists and starts the merging process
    if not os.path.isfile(zip_path):
        logging.error(f"The file {zip_path} does not exist.")
    else:
        # Initiates the main process of unzipping and merging
        if not main(zip_path, args.chunk_size, args.threads):
            logging.error("The merging process encountered errors.")
