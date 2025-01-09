import json
import csv
import os


def safe_deck_name(path):
    """Replaces only slashes with underscores while preserving existing underscores."""
    return path.replace("/", "__")  # Double underscore to avoid conflicts


def export_to_csv(input_dir, output_dir):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process each JSON file in topics
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".json"):
                # Derive deck and tag names
                relative_path = os.path.relpath(root, input_dir)  # e.g., linux/
                deck_name = safe_deck_name(relative_path)         # Avoid underscore conflicts
                tag_name = os.path.splitext(file)[0]              # File name → tag

                # Prepare output directory for deck
                deck_output_dir = os.path.join(output_dir, deck_name)
                os.makedirs(deck_output_dir, exist_ok=True)

                # Prepare output CSV for the deck
                output_file = os.path.join(deck_output_dir, f"{tag_name}.csv")

                with open(output_file, 'w', newline='') as csvfile:  # Overwrite mode for a clean start
                    writer = csv.writer(csvfile)
                    writer.writerow(["ID", "Front", "Back", "Tags"])  # Write headers

                    # Load JSON data
                    with open(os.path.join(root, file), 'r') as f:
                        data = json.load(f)
                        cards = data.get('cards', [])  # Support multiple cards
                        for card in cards:
                            # Construct full ID
                            card_id = f"{deck_name}-{tag_name}-{card['id']}"

                            # Combine tags
                            tags = ";".join(data.get('tags', [])) + f";{tag_name}"

                            # Write to CSV
                            writer.writerow([card_id, card['question'], card['answer'], tags])

                print(f"Exported deck: {deck_name}/{tag_name} → {output_file}")


if __name__ == "__main__":
    # Define paths
    input_dir = os.path.join(os.path.dirname(__file__), "../../topics")
    output_dir = os.path.join(os.path.dirname(__file__), "../../data")
    export_to_csv(input_dir, output_dir)

