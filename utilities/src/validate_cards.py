import json
import os
from jsonschema import validate, ValidationError

# Load the schema
SCHEMA_PATH = "./utilities/templates/flashcard_schema.json"
with open(SCHEMA_PATH, 'r') as schema_file:
    SCHEMA = json.load(schema_file)

def validate_json(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Validate using the schema
        validate(instance=data, schema=SCHEMA)
        return True, "Valid."
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"
    except ValidationError as e:
        return False, f"Schema validation error: {str(e)}"

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

