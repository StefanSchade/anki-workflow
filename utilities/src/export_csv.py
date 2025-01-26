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
    "<{start-ul}>": "<ul style=\"text-align: left;\">",
    "<{end-ul}>": "</ul>",    
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

def get_writer(output_file, writers):
    """Helper to fetch or create a CSV writer from the writers dict."""
    if output_file not in writers:
        csvfile = open(output_file, 'w', newline='')
        writer = csv.writer(csvfile)
        writers[output_file] = (writer, csvfile)
    return writers[output_file]

def export_to_csv(input_dir, output_dir):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process each JSON file in the topics directory
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".json"):
                # Derive deck and tag names
                relative_path = os.path.relpath(root, input_dir)  # e.g., linux/
                deck_name = safe_deck_name(relative_path)
                tag_name = os.path.splitext(file)[0]

                # Load JSON data
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cards = data.get('cards', [])

                # A dictionary to track CSV writers for each output file
                writers = {}

                # Process each card
                for card in cards:
                    card_type = card.get("type")
                    
                    if card_type in ["basic", "typing"]:
                        # old logic remains as-is
                        anki_type = "typing" if card_type == "typing" else "basic"
                        output_file = os.path.join(
                            output_dir, f"{deck_name}-{tag_name}-{anki_type}.csv")
                        writer, _ = get_writer(output_file, writers)

                        front = replace_custom_tags(card["question"]).replace("\n", "<br>")
                        back = replace_custom_tags(card.get("answer", "N/A")).replace("\n", "<br>")

                        # Add the filename tag (same as original code)
                        all_tags = card.get("tags", []) + [tag_name]
                        # For now, we only store the last one in the CSV's third column to match existing behavior
                        writer.writerow([front, back, tag_name])

                    elif card_type == "multiple-choice":
                        # old logic remains as-is
                        output_file = os.path.join(
                            output_dir, f"{deck_name}-{tag_name}-typing.csv")
                        writer, _ = get_writer(output_file, writers)
                        choices = card.get("choices", [])

                        front = replace_custom_tags(card["question"]).replace("\n", "<br>") + "<br><br>"
                        front += "<br>".join([f"{idx+1}. {c['text']}" for idx, c in enumerate(choices)])

                        correct_choices = [c for c in choices if c.get("correct")]
                        if correct_choices:
                            back = "Correct Answer(s):<br>"
                            back += "<br>".join(
                                [f"{idx+1}. {c['text']}: {c.get('explanation', 'No explanation provided.')}"
                                 for idx, c in enumerate(choices) if c.get("correct")])
                            back += "<br><br>Incorrect Answer(s):<br>"
                            back += "<br>".join(
                                [f"{idx+1}. {c['text']}: {c.get('explanation', 'No explanation provided.')}"
                                 for idx, c in enumerate(choices) if not c.get("correct")])
                        else:
                            back = "This was a trick question - there were no correct answers."

                        all_tags = card.get("tags", []) + [tag_name]
                        writer.writerow([front, back, tag_name])

                    elif card_type == "vocabulary":
                        # New logic for 'vocabulary' type
                        # Fields we expect: native (string), context (optional), foreign (array of {word, definition?})
                        native_term = card.get("native", "")
                        context = card.get("context")
                        foreign_list = card.get("foreign", [])  # list of dicts: [{word, definition?}, ...]

                        # We will produce up to three kinds of sub-cards:
                        # 1) Native -> Foreign (typing) (one card listing all foreign words as answer)
                        # 2) For each foreign word => Foreign -> Native (basic)
                        # 3) For each foreign word that has a definition => Definition -> Foreign (typing)

                        if not foreign_list:
                            # If foreign is empty or missing, skip
                            print(f"Skipping vocabulary card with no foreign words: {card.get('id')}")
                            continue

                        # (1) Native -> Foreign [typing card]
                        all_foreign_words = [item.get("word", "") for item in foreign_list if item.get("word")]
                        joined_foreign = ", ".join(all_foreign_words)

                        # Construct the question, e.g. "Translate to English: grün (Farbe)"
                        # or if context is not None => "grün (context)"
                        if context:
                            front_text = f"Translate to Foreign: {native_term} ({context})"
                        else:
                            front_text = f"Translate to Foreign: {native_term}"

                        # This is typed out by the user => 'typing' => 'basic (with typing)' in Anki
                        output_file_typing = os.path.join(
                            output_dir, f"{deck_name}-{tag_name}-typing.csv")
                        writer_typing, _ = get_writer(output_file_typing, writers)

                        front = replace_custom_tags(front_text)
                        back = replace_custom_tags(joined_foreign)

                        # Add the filename tag
                        all_tags = card.get("tags", []) + [tag_name]
                        writer_typing.writerow([front, back, tag_name])

                        # (2) Foreign -> Native [basic card], one per foreign word
                        # 'Translate to Native: <foreign>' => <native_term>
                        output_file_basic = os.path.join(
                            output_dir, f"{deck_name}-{tag_name}-basic.csv")
                        writer_basic, _ = get_writer(output_file_basic, writers)

                        for f_item in foreign_list:
                            foreign_word = f_item.get("word")
                            if not foreign_word:
                                continue
                            front_f2n = f"Translate to Native: {foreign_word}"
                            back_f2n = native_term
                            writer_basic.writerow([
                                replace_custom_tags(front_f2n),
                                replace_custom_tags(back_f2n),
                                tag_name
                            ])

                        # (3) Definition -> Foreign [typing card], for each foreign word that has a definition
                        for f_item in foreign_list:
                            definition = f_item.get("definition")
                            foreign_word = f_item.get("word")
                            if definition and foreign_word:
                                # question => definition, answer => foreign word => typed by user => 'typing'
                                writer_typing.writerow([
                                    replace_custom_tags(definition),
                                    replace_custom_tags(foreign_word),
                                    tag_name
                                ])

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
