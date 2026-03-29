import json
import sys
import os
import zipfile
import shutil
import http.server
import socketserver
import webbrowser
from jsonschema import validate, ValidationError

# Base directory for schemas
SCHEMA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'schema')

def load_schema(schema_name):
    schema_path = os.path.join(SCHEMA_DIR, f"{schema_name}.json")
    if not os.path.exists(schema_path):
        # Handle manifest naming fallback
        if schema_name == "manifest":
            schema_path = os.path.join(SCHEMA_DIR, "h3_manifest.json")
        
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
                return False, None
            
            # Check if it's an array of items or a single item
            items = data if isinstance(data, list) else [data]
            
            for i, item in enumerate(items):
                try:
                    validate(instance=item, schema=schema)
                except ValidationError as e:
                    prefix = f"Item #{i} " if isinstance(data, list) else ""
                    print(f"❌ {prefix}Validation Error: {e.message}")
                    return False, None
            
            count = len(items)
            print(f"✅ Validated {count} {'item' if count == 1 else 'items'} against '{entity_type}' schema.")
            return True, data
        else:
            print("✅ Valid JSON (no schema provided)")
            return True, data
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False, None

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

def check_integrity(package_dir):
    """Checks cross-reference integrity within an H3 package folder."""
    print(f"🔍 Checking integrity of package: {package_dir}")
    
    entities_dir = os.path.join(package_dir, 'entities')
    if not os.path.exists(entities_dir):
        # Fallback if the user just points to a folder with JSONs
        entities_dir = package_dir

    all_data = {}
    entity_files = {
        'building': 'buildings.json',
        'asset': 'assets.json',
        'space': 'spaces.json',
        'event': 'events.json',
        'contracts': 'contracts.json',
        'warranty': 'warranties.json'
    }

    # 1. Load and Validate all available entities
    for entity, filename in entity_files.items():
        path = os.path.join(entities_dir, filename)
        if os.path.exists(path):
            success, data = validate_h3(path, entity)
            if success:
                all_data[entity] = data if isinstance(data, list) else [data]

    if not all_data:
        print("⚠️ No entity files found to check.")
        return

    # 2. Cross-Reference Checks
    print("\n🔗 Running Cross-Reference Checks...")
    errors = 0

    # Collect all IDs for fast lookup
    building_ids = {b['building_id'] for b in all_data.get('building', [])}
    space_ids = {s['space_id'] for s in all_data.get('space', [])}
    asset_ids = {a['asset_id'] for a in all_data.get('asset', [])}

    # Check Assets -> Building/Space
    for asset in all_data.get('asset', []):
        if asset.get('building_id') not in building_ids:
            print(f"❌ Asset '{asset['asset_id']}' refers to missing Building '{asset['building_id']}'")
            errors += 1
        if asset.get('space_id') and asset.get('space_id') not in space_ids:
            print(f"❌ Asset '{asset['asset_id']}' refers to missing Space '{asset['space_id']}'")
            errors += 1

    # Check Warranties -> Assets
    for warranty in all_data.get('warranty', []):
        if warranty.get('asset_id') and warranty.get('asset_id') not in asset_ids:
            print(f"❌ Warranty '{warranty['warranty_id']}' refers to missing Asset '{warranty['asset_id']}'")
            errors += 1

    if errors == 0:
        print("✅ All cross-references are valid!")
    else:
        print(f"❌ Found {errors} integrity errors.")

def serve_viewer(port=8000):
    """Starts a local web server to view the dashboard."""
    root_dir = os.path.join(os.path.dirname(__file__), '..', '..')
    os.chdir(root_dir)
    
    Handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            url = f"http://localhost:{port}"
            print(f"🚀 H3 Dashboard active at: {url}")
            print("Press Ctrl+C to stop the server.")
            webbrowser.open(url)
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Could not start server: {e}")

def show_help():
    print("H3 Core CLI Tool")
    print("----------------")
    print("Commands:")
    print("  validate <file> [type]   Validate JSON against H3 schema")
    print("  pack <dir> [output]      Pack a folder into an .h3pkg container")
  print("  unpack <file> [dest]     Unpack an .h3pkg container")
  print("  check <dir>              Check cross-reference integrity of a package")
  print("  serve [port]             Start the visual dashboard viewer")
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
    elif cmd == "check" and len(sys.argv) >= 3:
        check_integrity(sys.argv[2])
    elif cmd == "serve":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        serve_viewer(port)
    else:
        show_help()
