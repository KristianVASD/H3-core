# H3 Adapter Interface

This document describes how external systems can integrate with H3.

---

## 🎯 Goal

Allow any system (ERP, VvE software, contractor platform) to:

* export data to H3
* import H3 packages

---

## 🔁 Export to H3

Steps:

1. Map internal data → H3 schemas
2. Generate entity JSON files
3. Create `manifest.json`
4. Bundle into `.h3pkg`

---

## 🔁 Import from H3

Steps:

1. Read `manifest.json`
2. Load entity files
3. Link files via `file_links.json`

---

## 🧩 Mapping Example

| Internal Field | H3 Field               |
| -------------- | ---------------------- |
| property_id    | building_id            |
| install_date   | lifecycle.installed_at |
| contractor     | supplier_id            |

---

## 🚀 Strategy

Start simple:

* export only assets + building

Then expand:

* events
* contracts
* warranties
