import json
import sys
import os
import zipfile
import shutil
import http.server
import socketserver
import webbrowser
from jsonschema import validate, ValidationError


def _reconfigure_stdio_utf8():
    """Avoid UnicodeEncodeError on Windows (cp1252) when printing CLI symbols."""
    if sys.platform != "win32":
        return
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, OSError, ValueError):
                pass


_reconfigure_stdio_utf8()

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

def _find_manifest_path(package_dir):
    package_dir = os.path.abspath(package_dir)
    for candidate in (
        os.path.join(package_dir, 'manifest.json'),
        os.path.join(package_dir, 'minimal_manifest.json'),
        os.path.join(package_dir, 'manifest', 'minimal_manifest.json'),
    ):
        if os.path.exists(candidate):
            return candidate
    return None


def _package_root_for_manifest(manifest_path):
    manifest_path = os.path.abspath(manifest_path)
    parent = os.path.dirname(manifest_path)
    if os.path.basename(parent) == 'manifest':
        return os.path.dirname(parent)
    return parent


def _load_source_registry(package_root, rel_path):
    """Load and schema-validate sources.json; returns (list|None, error_message|None)."""
    path = os.path.normpath(os.path.join(package_root, rel_path.replace('/', os.sep)))
    if not os.path.exists(path):
        return None, f"Sources registry not found at {path}"
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return None, f"Could not read sources registry: {e}"
    if not isinstance(data, list):
        return None, "Sources registry must be a JSON array"
    schema = load_schema('source')
    if schema:
        for i, item in enumerate(data):
            try:
                validate(instance=item, schema=schema)
            except ValidationError as e:
                return None, f"Sources item #{i}: {e.message}"
    ids = [item.get('source_id') for item in data if isinstance(item, dict)]
    if len(ids) != len(set(ids)):
        return None, "Duplicate source_id in sources registry"
    return data, None


def check_integrity(package_dir):
    """Checks cross-reference integrity within an H3 package folder."""
    print(f"🔍 Checking integrity of package: {package_dir}")

    entities_dir = os.path.join(package_dir, 'entities')
    if not os.path.exists(entities_dir):
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

    for entity, filename in entity_files.items():
        path = os.path.join(entities_dir, filename)
        if os.path.exists(path):
            success, data = validate_h3(path, entity)
            if success:
                all_data[entity] = data if isinstance(data, list) else [data]

    if not all_data:
        print("⚠️ No entity files found to check.")
        return

    print("\n🔗 Running Cross-Reference Checks...")
    errors = 0

    manifest_path = _find_manifest_path(package_dir)
    package_root = _package_root_for_manifest(manifest_path) if manifest_path else os.path.abspath(package_dir)
    source_ids = set()

    if manifest_path:
        ok, manifest = validate_h3(manifest_path, 'manifest')
        if not ok:
            errors += 1
        elif isinstance(manifest, dict):
            rel = manifest.get('sources')
            if not rel:
                print("❌ Manifest is missing required 'sources' (path to sources registry).")
                errors += 1
            else:
                sources_data, src_err = _load_source_registry(package_root, rel)
                if src_err:
                    print(f"❌ {src_err}")
                    errors += 1
                elif sources_data is not None:
                    source_ids = {s['source_id'] for s in sources_data if s.get('source_id')}
                    print(f"📎 Loaded {len(source_ids)} source(s) from manifest path '{rel}'.")
    else:
        fallback = os.path.join(entities_dir, 'sources.json')
        if os.path.exists(fallback):
            rel = os.path.relpath(fallback, package_root).replace(os.sep, '/')
            sources_data, src_err = _load_source_registry(package_root, rel)
            if src_err:
                print(f"❌ {src_err}")
                errors += 1
            elif sources_data is not None:
                source_ids = {s['source_id'] for s in sources_data if s.get('source_id')}
                print(f"📎 Loaded {len(source_ids)} source(s) from {fallback} (no manifest in tree).")

    building_ids = {b['building_id'] for b in all_data.get('building', [])}
    space_ids = {s['space_id'] for s in all_data.get('space', [])}
    asset_ids = {a['asset_id'] for a in all_data.get('asset', [])}

    for asset in all_data.get('asset', []):
        if asset.get('building_id') not in building_ids:
            print(f"❌ Asset '{asset['asset_id']}' refers to missing Building '{asset['building_id']}'")
            errors += 1
        if asset.get('space_id') and asset.get('space_id') not in space_ids:
            print(f"❌ Asset '{asset['asset_id']}' refers to missing Space '{asset['space_id']}'")
            errors += 1

    for warranty in all_data.get('warranty', []):
        if warranty.get('asset_id') and warranty.get('asset_id') not in asset_ids:
            print(f"❌ Warranty '{warranty['warranty_id']}' refers to missing Asset '{warranty['asset_id']}'")
            errors += 1

    def any_evidence():
        for asset in all_data.get('asset', []):
            if asset.get('evidence'):
                return True
        for event in all_data.get('event', []):
            if event.get('evidence'):
                return True
        return False

    if any_evidence():
        print("\n🛡️ Evidence / source referential checks...")
        if not source_ids:
            print("❌ Entities declare evidence but no valid sources registry was loaded.")
            errors += 1
        else:
            for asset in all_data.get('asset', []):
                for ev in asset.get('evidence') or []:
                    sid = ev.get('source_id')
                    if sid and sid not in source_ids:
                        print(f"❌ Asset '{asset['asset_id']}' evidence references unknown source_id '{sid}'")
                        errors += 1
            for event in all_data.get('event', []):
                for ev in event.get('evidence') or []:
                    sid = ev.get('source_id')
                    if sid and sid not in source_ids:
                        eid = event.get('event_id', '?')
                        print(f"❌ Event '{eid}' evidence references unknown source_id '{sid}'")
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
    print("  building, asset, space, event, contracts, warranty, manifest, source")

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
