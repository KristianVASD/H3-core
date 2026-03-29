# Example H3 Package Structure

```
woning-001.h3pkg
│
├── manifest.json
│
├── entities/
│   ├── buildings.json
│   ├── assets.json
│   ├── events.json
│   ├── contracts.json
│   └── warranties.json
│
├── files/
│   ├── manuals/
│   │   └── boiler_manual.pdf
│   ├── photos/
│   │   └── door_issue.jpg
│   └── invoices/
│
├── links/
│   └── file_links.json
│
└── meta/
    └── package.json
```

---

## Notes

* `manifest.json` is always required
* All paths are relative
* Files are optional, but recommended
* Entities must follow H3 schemas

---

## Minimal Package

```
minimal.h3pkg
├── manifest.json
└── entities/
    ├── buildings.json
    └── assets.json
```
