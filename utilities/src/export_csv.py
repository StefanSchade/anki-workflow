import json
import csv
import os

def export_to_csv(input_dir, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Front", "Back"])  # Header

        # Traverse input directory
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        cards = json.load(f)
                        for card in cards['fields']:
                            writer.writerow([card['question'], card['answer']])
    print(f"Exported to {output_file}")

if __name__ == "__main__":
    input_dir = "../topics"
    output_file = "../data/cards.csv"
    export_to_csv(input_dir, output_file)

