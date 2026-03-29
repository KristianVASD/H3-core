import json
import sys
import os
import zipfile
import shutil
from jsonschema import validate, ValidationError

# Base directory for schemas
SCHEMA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'schema')

def load_schema(schema_name):
    schema_path = os.path.join(SCHEMA_DIR, f"{schema_name}.json")
    if not os.path.exists(schema_path):
        # Handle common naming/typo fallbacks
        fallbacks = {
            "warranty": "warrenty",
            "manifest": "h3_manifest"
        }
        schema_path = os.path.join(SCHEMA_DIR, f"{fallbacks.get(schema_name, schema_name)}.json")
        if not os.path.exists(schema_path):
            return None
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_h3(file_path, entity_type=None):
    """Validates an H3 JSON file against its schema."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if entity_type:
            schema = load_schema(entity_type)
            if not schema:
                print(f"❌ Schema for '{entity_type}' not found.")
                return False
            
            # Check if it's an array of items or a single item
            items = data if isinstance(data, list) else [data]
            
            for i, item in enumerate(items):
                try:
                    validate(instance=item, schema=schema)
                except ValidationError as e:
                    prefix = f"Item #{i} " if isinstance(data, list) else ""
                    print(f"❌ {prefix}Validation Error: {e.message}")
                    return False
            
            count = len(items)
            print(f"✅ Validated {count} {'item' if count == 1 else 'items'} against '{entity_type}' schema.")
        else:
            print("✅ Valid JSON (no schema provided)")
        return True
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False

def pack_h3(source_dir, output_file=None):
    """Packs a directory into an .h3pkg file."""
    if not output_file:
        output_file = f"{os.path.basename(os.path.abspath(source_dir))}.h3pkg"
    
    if not os.path.exists(os.path.join(source_dir, 'manifest.json')) and \
       not os.path.exists(os.path.join(source_dir, 'minimal_manifest.json')):
        print("⚠️ Warning: No manifest found in the source directory.")

    try:
        # Create zip archive and rename to .h3pkg
        base_name = output_file.replace('.h3pkg', '')
        shutil.make_archive(base_name, 'zip', source_dir)
        os.rename(f"{base_name}.zip", output_file)
        print(f"📦 Successfully created H3 Package: {output_file}")
    except Exception as e:
        print(f"❌ Error packing: {e}")

def unpack_h3(pkg_file, dest_dir=None):
    """Unpacks an .h3pkg file into a directory."""
    if not dest_dir:
        dest_dir = pkg_file.replace('.h3pkg', '_unpacked')
    
    try:
        with zipfile.ZipFile(pkg_file, 'r') as zip_ref:
            zip_ref.extractall(dest_dir)
        print(f"🔓 Successfully unpacked {pkg_file} to {dest_dir}")
    except Exception as e:
        print(f"❌ Error unpacking: {e}")

def show_help():
    print("H3 Core CLI Tool")
    print("----------------")
    print("Commands:")
    print("  validate <file> [type]   Validate JSON against H3 schema")
    print("  pack <dir> [output]      Pack a folder into an .h3pkg container")
    print("  unpack <file> [dest]     Unpack an .h3pkg container")
    print("\nEntity types for validation:")
    print("  building, asset, space, event, contracts, warranty, manifest")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    cmd = sys.argv[1]
    
    if cmd == "validate" and len(sys.argv) >= 3:
        validate_h3(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == "pack" and len(sys.argv) >= 3:
        pack_h3(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == "unpack" and len(sys.argv) >= 3:
        unpack_h3(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    else:
        show_help()
