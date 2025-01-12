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
                relative_path = os.path.relpath(root, input_dir)  # e.g., linux/
                deck_name = safe_deck_name(relative_path)         # Avoid underscore conflicts
                tag_name = os.path.splitext(file)[0]              # File name → tag

                deck_output_dir = os.path.join(output_dir, deck_name)
                os.makedirs(deck_output_dir, exist_ok=True)

                output_file = os.path.join(deck_output_dir, f"{tag_name}.csv")

                with open(output_file, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)

                    with open(os.path.join(root, file), 'r') as f:
                        data = json.load(f)
                        cards = data.get('cards', [])
                        for card in cards:
                            tags = ";".join(data.get('tags', [])) + f";{tag_name}"

                            if card['type'] == 'multiple-choice':
                                # Generate the Front
                                choices = card.get('choices', [])
                                front = card['question'] + "\n\n"
                                front += "\n".join([f"{idx+1}. {choice['text']}" for idx, choice in enumerate(choices)])
                                front += "\n\nPlease give the number(s) of the correct answer(s), separated by spaces."

                                # Generate the Back
                                correct_answers = [str(idx+1) for idx, choice in enumerate(choices) if choice['correct']]
                                if correct_answers:
                                    back = f"Correct Answer(s): {' '.join(correct_answers)}\n\n"
                                    back += "Explanations:\n"
                                    for idx, choice in enumerate(choices):
                                        explanation = choice.get('explanation', "No explanation provided.")
                                        back += f"{idx+1}. {choice['text']}: {explanation}\n"
                                else:
                                    back = "This was a trick question - there was no correct answer."

                            else:
                                # Handle other card types
                                front = card.get('question', "N/A")
                                back = card.get('answer', "N/A")

                            # Replace line breaks with <br>
                            front = front.replace("\n", "<br>")
                            back = back.replace("\n", "<br>")

                            writer.writerow([front, back, tags])

                print(f"Exported deck: {deck_name}/{tag_name} → {output_file}")


if __name__ == "__main__":
    # Define default paths for input and output
    input_dir = "./topics"
    output_dir = "./data"
    export_to_csv(input_dir, output_dir)
