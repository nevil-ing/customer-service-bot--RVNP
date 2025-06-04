import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")

INPUT_FILES_TO_COMBINE = [
    "rvist_data.jsonl",
    "hef_data_for_rag.jsonl",
]

# Name of the output combined file
COMBINED_OUTPUT_FILE = "combined_rag_data.jsonl"
output_file_path = os.path.join(DATASET_DIR, COMBINED_OUTPUT_FILE)

def combine_jsonl_files():
    """
    Reads multiple .jsonl files from the DATASET_DIR and combines them
    into a single output .jsonl file in the same directory.
    """
    print(f"Combining JSONL files into: {output_file_path}")
    
    # Ensure dataset directory exists 
    if not os.path.exists(DATASET_DIR):
        print(f"Error: Dataset directory '{DATASET_DIR}' not found.")
        return

    record_count = 0
    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        for filename in INPUT_FILES_TO_COMBINE:
            input_file_path = os.path.join(DATASET_DIR, filename)
            print(f"Processing file: {input_file_path}...")
            try:
                with open(input_file_path, 'r', encoding='utf-8') as infile:
                    for line_number, line in enumerate(infile, 1):
                        line_content = line.strip()
                        if not line_content: # Skip empty lines
                            continue
                        try:
                            # Validate if it's JSON, just in case
                            json.loads(line_content) 
                            outfile.write(line_content + '\n') 
                            record_count += 1
                        except json.JSONDecodeError as e:
                            print(f"  Skipping invalid JSON line #{line_number} in {filename}: {e} - Content: '{line_content[:100]}...'")
                print(f"  Finished processing {filename}.")
            except FileNotFoundError:
                print(f"  Warning: File {filename} not found in {DATASET_DIR}. Skipping.")
            except Exception as e:
                print(f"  An error occurred while processing {filename}: {e}")

    if record_count > 0:
        print(f"\nSuccessfully combined {record_count} records into {COMBINED_OUTPUT_FILE}.")
    else:
        print(f"\nNo records were combined. Check if input files exist and contain data.")

if __name__ == "__main__":
    combine_jsonl_files()