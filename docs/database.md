# H3 Database Model (Conceptual)

H3 is database-agnostic.

However, a typical implementation maps entities to tables:

---

## Core Tables

* buildings
* spaces
* assets
* events
* contracts
* warranties

---

## Relationships

* assets → building_id
* events → asset_id
* warranties → asset_id
* contracts → building_id

---

## Files

Files are not stored in the database.

Instead:

* stored in object storage
* linked via `file_links.json`

---

## Why not enforce a database?

H3 is designed to:

* work with any backend
* be transportable
* remain future-proof

---

## Recommended Stack

* PostgreSQL (structured data)
* Object storage (files)
* JSONB for flexibility

---

## Closed Layer (DossierMind)

The AI layer adds:

* knowledge graph
* embeddings
* inference results

This is not part of H3 Core.
