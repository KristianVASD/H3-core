# H3 Package Specification (.h3pkg)

The `.h3pkg` file is the standard container for building data. It is a ZIP-compressed archive containing structured JSON data, raw files, and a manifest that links them together.

## 📁 File Structure

Every H3 Package MUST follow this internal structure:

```text
building-name.h3pkg/
├── manifest.json       # REQUIRED: The entry point and index
├── entities/           # Data files for building, assets, etc.
│   ├── building.json
│   ├── assets.json
│   └── ...
├── files/              # Binary files (PDFs, Images, BIM, etc.)
│   ├── warranty_a.pdf
│   └── photo_b.jpg
├── links/              # Optional: Relations between files and data
└── meta/               # Package metadata and signatures
```

## 📄 The Manifest (manifest.json)

The manifest is the "brain" of the package. It defines what version of H3 is used and lists all entities included.

```json
{
  "h3_version": "1.0",
  "package_id": "pkg_12345",
  "created_at": "2024-03-29T12:00:00Z",
  "entities": {
    "building": "entities/building.json",
    "assets": "entities/assets.json"
  }
}
```

## 🔗 Extension Pattern (metadata)

To ensure the standard remains flexible, every entity schema includes a `metadata` object. This is where proprietary or industry-specific data should live.

**Standard Practice:**
Use a namespace prefix for your custom fields to avoid collisions.
```json
"metadata": {
  "dossiermind:ai_confidence": 0.98,
  "solarco:panel_efficiency": "22%"
}
```

## 🛠️ Integrity Rules

1. **Self-Contained**: All files referenced in `entities/` MUST exist within the `files/` directory of the same package.
2. **ID Uniqueness**: All IDs (building_id, asset_id) MUST be unique within the package scope.
3. **Schema Compliance**: All JSON files in `entities/` MUST validate against the official H3 Core schemas.
