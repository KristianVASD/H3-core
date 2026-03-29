# H3 Package (.h3pkg)

The `.h3pkg` format is the standard container for exchanging building data.

It bundles structured data, files, and relationships into one portable package.

---

## 📦 What is a .h3pkg?

A `.h3pkg` file is simply a ZIP archive with a defined structure:

* `manifest.json` → entry point
* `/entities/` → structured data
* `/files/` → original documents
* `/links/` → file-to-entity relationships

---

## 🎯 Purpose

* Share building data between systems
* Preserve context (files + structure)
* Enable AI processing
* Prevent data loss

---

## 🔁 Typical Flow

1. Source system exports data → `.h3pkg`
2. Target system reads `manifest.json`
3. Entities are loaded
4. Files are linked via `/links/file_links.json`

---

## 🧠 Why this matters

Without a package format:

* data is fragmented
* files lose context
* AI cannot reason properly

With `.h3pkg`:

* everything stays connected
* systems can interoperate
* AI can understand reality

---

## 📌 Design Principles

* Simple (ZIP-based)
* Transparent (JSON)
* Extensible (future-proof)
* Tool-independent

---

## 🚀 Future

`.h3pkg` can become:

* the standard for real estate transactions
* the backbone of digital twins
* the input layer for AI building agents
