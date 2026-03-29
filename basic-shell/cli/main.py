import json
import sys
import os
from jsonschema import validate, ValidationError

# Base directory for schemas
SCHEMA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'schema')

def load_schema(schema_name):
    schema_path = os.path.join(SCHEMA_DIR, f"{schema_name}.json")
    if not os.path.exists(schema_path):
        # Handle typo fallback
        if schema_name == "warranty":
            schema_path = os.path.join(SCHEMA_DIR, "warrenty.json")
        else:
            return None
    
    with open(schema_path, 'r') as f:
        return json.load(f)

def validate_h3(file_path, entity_type=None):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if entity_type:
            schema = load_schema(entity_type)
            if not schema:
                print(f"❌ Schema for '{entity_type}' not found.")
                return False
            
            try:
                validate(instance=data, schema=schema)
                print(f"✅ Valid H3 {entity_type.capitalize()}")
            except ValidationError as e:
                print(f"❌ Validation Error: {e.message}")
                return False
        else:
            print("✅ Valid JSON (no schema validation performed)")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_help():
    print("H3 Core CLI")
    print("Usage:")
    print("  python main.py validate <file_path> [entity_type]")
    print("\nAvailable entity types:")
    print("  building, asset, space, event, contracts, warranty, h3_manifest")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        show_help()
        sys.exit(1)

    command = sys.argv[1]
    path = sys.argv[2]
    entity = sys.argv[3] if len(sys.argv) > 3 else None

    if command == "validate":
        validate_h3(path, entity)
    else:
        show_help()
