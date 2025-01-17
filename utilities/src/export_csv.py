import json
import csv
import os

# Define custom tag replacements
tag_replacements = {
    "<{start-terminal}>": "<div style=\"font-family: 'Courier New', monospace; background-color: #000; color: #00ff00; padding: 5px; border-radius: 3px; white-space: pre-wrap; text-align: left;\">",
    "<{end-terminal}>": "</div>",
    "<{start-bold}>": "<b>",
    "<{end-bold}>": "</b>",
    "<{start-h1}>": "<h1 style='text-align: left;'>",
    "<{end-h1}>": "</h1>",
    "<{start-h2}>": "<h2 style='text-align: left;'>",
    "<{end-h2}>": "</h2>",
    "<{start-h3}>": "<h3 style='text-align: left;'>",
    "<{end-h3}>": "</h3>",
     "<{start-h4}>": "<h4 style='text-align: left;'>",
    "<{end-h4}>": "</h4>",
    "<{start-h5}>": "<h5 style='text-align: left;'>",
    "<{end-h5}>": "</h5>",
    "<{start-h6}>": "<h6 style='text-align: left;'>",
    "<{end-h6}>": "</h6>",
    "<{bullet-item}>": "<li>",
    "<{end-bullet-item}>": "</li>",
    "<{start-table}>": "<table>",
    "<{end-table}>": "</table>",
    "<{start-tr}>": "<tr>",
    "<{end-tr}>": "</tr>",
    "<{start-td}>": "<td>",
    "<{end-td}>": "</td>",
    "<{start-numbered-item}>": "<li>",
    "<{end-numbered-item}>": "</li>",
    "<{start-ol}>": "<ol style=\"text-align: left;\">",
    "<{end-ol}>": "</ol>",
    "<{break}>": "<br>",
}

def safe_deck_name(path):
    """Replaces slashes with double underscores to avoid conflicts."""
    return path.replace("/", "__")

def replace_custom_tags(text):
    """Replace custom tags with styled HTML elements."""
    for tag, replacement in tag_replacements.items():
        text = text.replace(tag, replacement)
    return text

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

                        # Replace custom tags in question and answer
                        front = replace_custom_tags(card["question"]).replace("\n", "<br>")
                        back = replace_custom_tags(card.get("answer", "N/A")).replace("\n", "<br>")

                        # Add the filename tag to the existing tags
                        all_tags = card.get("tags", []) + [tag_name]

                        writer.writerow([front, back, tag_name])

                    elif card_type == "multiple-choice":
                        output_file = os.path.join(output_dir, f"{deck_name}-{tag_name}-typing.csv")
                        if output_file not in writers:
                            csvfile = open(output_file, 'w', newline='')
                            writer = csv.writer(csvfile)
                            writers[output_file] = (writer, csvfile)

                        writer, _ = writers[output_file]
                        choices = card.get("choices", [])
                        front = replace_custom_tags(card["question"]).replace("\n", "<br>") + "<br><br>"
                        front += "<br>".join([f"{idx+1}. {choice['text']}" for idx, choice in enumerate(choices)])

                        correct_choices = [choice for idx, choice in enumerate(choices) if choice.get("correct")]
                        incorrect_choices = [choice for idx, choice in enumerate(choices) if not choice.get("correct")]

                        if correct_choices:
                            back = "Correct Answer(s):<br>"
                            back += "<br>".join([f"{idx+1}. {choice['text']}: {choice.get('explanation', 'No explanation provided.')}"
                                                 for idx, choice in enumerate(choices) if choice.get("correct")])
                            back += "<br><br>Incorrect Answer(s):<br>"
                            back += "<br>".join([f"{idx+1}. {choice['text']}: {choice.get('explanation', 'No explanation provided.')}"
                                                 for idx, choice in enumerate(choices) if not choice.get("correct")])
                        else:
                            back = "This was a trick question - there were no correct answers."

                        # Add the filename tag to the existing tags
                        all_tags = card.get("tags", []) + [tag_name]

                        writer.writerow([front, back, tag_name])

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

