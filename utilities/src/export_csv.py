import json
import csv
import os

def safe_deck_name(path):
    """Replaces slashes with double underscores to avoid conflicts."""
    return path.replace("/", "__")

def export_to_csv(input_dir, output_dir):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process each JSON file in the topics directory
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".json"):
                # Derive deck and tag names
                relative_path = os.path.relpath(root, input_dir)  # e.g., linux/
                deck_name = safe_deck_name(relative_path)         # Avoid underscore conflicts
                tag_name = os.path.splitext(file)[0]              # File name → tag

                # Load JSON data
                with open(os.path.join(root, file), 'r') as f:
                    data = json.load(f)
                    cards = data.get('cards', [])

                # Create a dictionary to track CSV writers for each output file
                writers = {}

                # Process each card
                for card in cards:
                    card_type = card.get("type")

                    if card_type in ["basic", "typing"]:
                        anki_type = "typing" if card_type == "typing" else "basic"
                        output_file = os.path.join(output_dir, f"{deck_name}-{tag_name}-{anki_type}.csv")
                        if output_file not in writers:
                            csvfile = open(output_file, 'w', newline='')
                            writer = csv.writer(csvfile)
                            writers[output_file] = (writer, csvfile)

                        writer, _ = writers[output_file]
                        front = card["question"].replace("\n", "<br>")
                        back = card.get("answer", "N/A").replace("\n", "<br>")

                        # Add the filename tag to the existing tags
                        all_tags = card.get("tags", []) + [tag_name]
                        tags_str = ";".join(all_tags)

                        writer.writerow([front, back, tags_str])

                    elif card_type == "multiple-choice":
                        output_file = os.path.join(output_dir, f"{deck_name}-{tag_name}-typing.csv")
                        if output_file not in writers:
                            csvfile = open(output_file, 'w', newline='')
                            writer = csv.writer(csvfile)
                            writers[output_file] = (writer, csvfile)

                        writer, _ = writers[output_file]
                        choices = card.get("choices", [])
                        front = card["question"].replace("\n", "<br>") + "<br><br>"
                        front += "<br>".join([f"{idx+1}. {choice['text']}" for idx, choice in enumerate(choices)])
                        back = "Correct Answer(s): "
                        correct_answers = [str(idx+1) for idx, choice in enumerate(choices) if choice.get("correct")]
                        back += ", ".join(correct_answers) + "<br><br>"
                        back += "Explanations:<br>"
                        back += "<br>".join([f"{idx+1}. {choice['text']}: {choice.get('explanation', 'No explanation provided.')}" for idx, choice in enumerate(choices)])

                        # Add the filename tag to the existing tags
                        all_tags = card.get("tags", []) + [tag_name]
                        tags_str = ";".join(all_tags)

                        writer.writerow([front, back, tags_str])

                    else:
                        print(f"Skipping unknown card type: {card_type}")

                # Close all CSV files
                for _, csvfile in writers.values():
                    csvfile.close()

                print(f"Exported deck: {deck_name}-{tag_name} → {', '.join(writers.keys())}")

if __name__ == "__main__":
    input_dir = "./topics"
    output_dir = "./data"

    export_to_csv(input_dir, output_dir)

