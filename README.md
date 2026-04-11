# H3 Core — The Open Standard for Building Context

**H3** is the universal open data standard for structuring everything about a building:
assets, events, maintenance, contracts and warranties.

It transforms fragmented data (Excel, PDFs, MJOPs, opleverdossiers) into one clean, portable, AI-ready format.

---

## 🧠 The Idea

Buildings today have **no memory**.

Data is scattered across:

* PDFs
* emails
* Excel sheets
* contractor systems

H3 introduces a **Shared Memory for Buildings**.

> One structure. One language. Forever usable.

---

## ⚡ What is H3?

H3 consists of two layers:

### 🔓 H3 Core (Open Source)

* JSON schemas (the language)
* `.h3pkg` package format
* Basic Shell (CLI + demo viewer)
* Fully free (Apache 2.0)

### 🔒 H3 Engine (Closed – DossierMind)

* AI ingestion (“upload anything”)
* Automatic timeline + maintenance plans
* Contractor matching
* Hebbian Reality Learning

---

## 🆚 Open vs Closed

| Aspect       | Open Source (H3 Core)        | Closed (H3 Engine)                |
| ------------ | ---------------------------- | --------------------------------- |
| Purpose      | Data structure + basic tools | Intelligence layer                |
| Import       | Structured JSON / Excel      | Any file (PDF, ZIP, images, etc.) |
| Intelligence | None                         | Full AI                           |
| Learning     | None                         | Hebbian learning                  |
| Cost         | Free forever                 | Paid                              |

---

## 📦 The H3 Package (.h3pkg)

The `.h3pkg` file is the **standard container for building data**.

Think of it as:

> 📄 “The PDF of buildings — but structured and AI-ready”

### Structure

```
my-building.h3pkg
├── manifest.json
├── entities/
├── files/
├── links/
└── meta/
```

---

## 📄 Manifest (the core of everything)

Every package contains a `manifest.json`:

It defines:

* what entities exist
* where files are located
* how everything connects

👉 This is the **entry point for every system and AI**.

---

## 🔗 Linking files to data

H3 connects raw files to structured data:

Example:

```json
{
  "file_path": "files/manuals/door_closer.pdf",
  "entity_type": "asset",
  "entity_id": "NL.BAG.123:door_closer:001"
}
```

This enables:

* traceability
* explainable AI
* lifecycle tracking

---

## The Evidence Layer (Source-Aware Data)

In H3, an asset does not merely “exist” in a spreadsheet or UI: it is an **observation** that can be tied back to **where it came from**. By appending an optional `evidence` array to entities such as assets and events, H3 models a **forensic chain of trust** from raw material (PDF, drawing, photo, sensor export, or explicit user input) through to the structured record and the timeline.

Each evidence item points at a `source_id` registered in the package’s **sources registry** (`sources` in the manifest → typically `entities/sources.json`). That registry stores the digital passport of each ingested file (`file_path` under `files/` in the `.h3pkg`, type, ingestion time, description). Together, **sources + evidence** make the format suitable for traceability, explainable AI (XAI), and audit-ready dossiers—without forcing a single rigid hierarchy; flat entities plus relationships plus provenance reflect how real building data actually arrives over time.

---

## 🚀 Quick Start

### 1. Open the demo

```bash
open index.html
```

### 2. Validate a manifest

```bash
h3 validate manifest/minimal_manifest.json
```

### 3. Explore schemas

```
/schema/
```

---

## 🧱 Repository Structure

* `/schema/` → official data standard
* `/manifest/` → example building datasets
* `/entities/` → sample structured data
* `/links/` → file-to-entity relationships
* `/package/` → `.h3pkg` specification
* `/basic-shell/` → CLI + demo tools
* `/interfaces/` → integration specs

---

## 🧪 Example Use Case

1. A homeowner receives a **new-build ZIP dossier**
2. It is converted into an `.h3pkg`
3. The user opens it in H3 Basic Shell
4. Everything is structured instantly:

   * assets
   * warranties
   * events
   * maintenance timeline

---

## 🔮 Vision

Every building will have:

* a **digital twin**
* a **living memory**
* an **AI brain**

H3 is the **foundation layer**.

---

## 🤝 Contributing

We welcome:

* schema improvements
* adapters
* real-world examples

Please open an issue first for major changes.

---

## 📜 License

Apache 2.0 — free for commercial and private use.

---

## ❤️ Final Note

H3 is not a product.

It is infrastructure.

A shared language for buildings —
so that data never gets lost again.
