import json
import os

def validate_json(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Validate required keys
        if 'type' not in data or 'fields' not in data:
            return False, "Missing 'type' or 'fields'."

        # Validate fields
        for field in data['fields']:
            if 'question' not in field or 'answer' not in field:
                return False, f"Field error in {file_path}."

        return True, "Valid."
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"

def check_all_topics():
    base_dir = "../topics"
    errors = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".json"):
                path = os.path.join(root, file)
                valid, msg = validate_json(path)
                if not valid:
                    errors.append(f"{path}: {msg}")
    if errors:
        print("Errors found:")
        for err in errors:
            print(err)
    else:
        print("All files are valid.")

if __name__ == "__main__":
    check_all_topics()

