import argparse
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import logging

# Set up basic logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

def run_merge(files_to_merge, output_file):
    """
    Executes the CycloneDX merge command for a list of files.
    """
    try:
        subprocess.run(['cyclonedx', 'merge', '--input-files'] + files_to_merge + ['--output-file', output_file], check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error in file {output_file}: {e}")
        return False
    return True

def split_into_chunks(lst, n):
    """
    Splits a list into chunks of size n.
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def main(dir_path, chunk_size, num_threads):
    """
    Main function to merge SBOM files.
    """
    files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith('.xml')]
    
    file_chunks = list(split_into_chunks(files, chunk_size))
    intermediate_files = [f"intermediate_{i}.xml" for i in range(len(file_chunks))]

    # Check for existing intermediate files to skip reprocessing
    existing_intermediates = [f for f in intermediate_files if os.path.exists(os.path.join(dir_path, f))]
    if existing_intermediates:
        logging.info("Skipping existing intermediate files.")
        file_chunks = [chunk for i, chunk in enumerate(file_chunks) if intermediate_files[i] not in existing_intermediates]

    success = True
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_chunk = {executor.submit(run_merge, chunk, os.path.join(dir_path, intermediate)): chunk for chunk, intermediate in zip(file_chunks, intermediate_files) if intermediate not in existing_intermediates}

        with tqdm(total=len(future_to_chunk), desc="Merging Files", unit="chunk") as progress:
            for future in as_completed(future_to_chunk):
                if not future.result():
                    success = False
                progress.update(1)

    if success:
        final_output = os.path.join(dir_path, "final_merged.xml")
        all_intermediates = [os.path.join(dir_path, f) for f in intermediate_files]
        if not run_merge(all_intermediates, final_output):
            success = False

    return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge SBOM XML files using CycloneDX.")
    parser.add_argument('--directory', '-d', help="Directory containing SBOM XML files.")
    parser.add_argument('--chunk-size', type=int, default=5, help="Number of files to process in each batch.")
    parser.add_argument('--threads', type=int, default=4, help="Number of parallel threads to use.")

    args = parser.parse_args()

    if args.directory:
        dir_path = args.directory
    else:
        dir_path = input("Enter the directory path containing SBOM XML files: ")

    if not os.path.isdir(dir_path):
        logging.error(f"The directory {dir_path} does not exist.")
    else:
        if not main(dir_path, args.chunk_size, args.threads):
            logging.error("The merging process encountered errors.")
