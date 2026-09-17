# Errors

## [ERR-20260728-001] docx_xml_text_replacement

**Logged**: 2026-07-28T00:00:00+02:00
**Priority**: low
**Status**: resolved
**Area**: docs

### Summary
Exact DOCX XML replacement failed because the closing quotation mark in the Word file differed from the Markdown source.

### Error

```text
RuntimeError: Expected one occurrence, found 0: Zriaďuje sa Rozhodcovská komisia (ďalej „Komisia") ako odborný orgán FEBUS pre rozhodcovskú agendu.
```

### Context

- The updater validates every original passage before rewriting the DOCX archive.
- The failed validation prevented any modification of the Word file.

### Suggested Fix

Inspect the exact paragraph text extracted from `word/document.xml`, update the expected source string, and rerun the all-or-nothing replacement.

### Metadata

- Reproducible: yes
- Related Files: FEBUS_smernica_o_rozhodcoch_navrh.docx, .tmp_update_directive_docx.py

### Resolution

- **Resolved**: 2026-07-28T00:00:00+02:00
- **Notes**: Matched the XML-escaped quotation mark and the separately formatted bold text run; all 20 replacements then completed atomically.

---
