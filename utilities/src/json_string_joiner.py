import re
import sys

def clean_multiline_strings(input_file, output_file):
    try:
        # Read the content of the input file
        with open(input_file, "r") as infile:
            content = infile.read()

        # We will repeatedly apply the regex until no more matches occur
        # The pattern looks for two adjacent string literals separated by whitespace/newlines:
        #     "..."\s*\n\s*"..."
        # Then merges them into one: "... ..."
        merged = True
        while merged:
            new_content, merged_count = re.subn(
                r'"([^"]*)"\s*\n\s*"([^"]*)"',
                r'"\1\2"',
                content
            )
            if merged_count > 0:
                content = new_content
            else:
                merged = False

        # Write the cleaned content to the output file
        with open(output_file, "w") as outfile:
            outfile.write(content)

        print(f"Successfully cleaned and saved JSON to {output_file}")

    except FileNotFoundError:
        print(f"Error: The file {input_file} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python json_string_joiner.py <input_file> <output_file>")
        print("\nDescription:")
        print("This script cleans multiline strings in a JSON file by joining them into single-line strings.")
        print("\nArguments:")
        print("  <input_file>: The path to the input JSON file with potentially broken multiline strings.")
        print("  <output_file>: The path where the cleaned JSON will be saved.")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        clean_multiline_strings(input_file, output_file)

