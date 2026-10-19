# Syllabus collection plan

Prepared: 2026-10-19. Scope confirmed by the user: a repeatable Python script for 100+ syllabus PDFs, first checked against the supplied Web Development Laboratory sample.

## 1. Extract only these academic fields

| Field | Handling |
| --- | --- |
| Course code, title, type, credit | Keep the source wording. For example, title `Web Development` and type `Laboratory` remain separate. |
| Prerequisites, corequisites | Keep explicit `None` as text; an absent value is JSON `null` and is flagged. |
| Course description | Keep the complete paragraph. Join line wraps without rewriting the content. |
| Course learning outcomes | Keep each CLO identifier and its complete text. |
| Learning plan | Keep the period headings and their Course Learning Outcomes / Topic Learning Outcomes overview tables, including continuation onto another page. Preserve additional outcome text such as the sample's collaboration bullet. |

**Exclude the week-by-week tables:** no module schedule, weeks, dates, activities, assessments, technology-enabler columns or allocated hours. Exclude professor/contact details, institutional vision/mission, grading, policies, references and signatures. Tools mentioned inside an included description/outcome remain part of that text.

The overview places CLOs and TLOs in two columns within a period. Preserve those two lists; do not invent one-to-one CLO/TLO links from their vertical positions. Do not derive skills, curriculum placement, program or track in this collection step.

## 2. Small implementation

Use one script, [extract_syllabi.py](../../scripts/extract_syllabi.py), with `pdfplumber` for text and bordered tables. The sample is text-native; OCR and external AI are unnecessary for this test. `pdfplumber` provides table bounding boxes and separate cell text, which avoids mixing the CLO/TLO columns. [Library documentation](https://github.com/jsvine/pdfplumber).

1. Read one PDF at a time. Extract the labelled course fields and the description/CLO sections.
2. Find the learning-plan overview tables by their two column headings and the preceding period heading. Carry a matching table continuation from the bottom of one page to the top of the next. Ignore weekly tables.
3. Save one UTF-8 `<original-filename>.pdf.json` file per PDF, with nested outcomes/periods. JSON is the proposed collection format because a single CSV row cannot preserve these lists cleanly. Keep the PDFs as the source of record.
4. Include only small collection metadata: source filename, SHA-256, page count, extractor/library version and section page references.
5. Check that every requested field exists, outcome identifiers are unique within each list, and each period contains CLOs/TLOs. Flag unfamiliar/missing structures as `needs_review`; record unreadable PDFs as `failed`. An `ok` status means these structural checks passed, not independently proven extraction accuracy.
6. Accept either one PDF or a folder recursively. Preserve relative subfolders in output names so identically named files do not overwrite one another. A bad PDF must not stop the remaining batch. Write a summary for that invocation and return a nonzero exit code if any file needs attention.

No database, web service, scheduler or model pipeline is needed. Re-running the same input/output paths replaces the derived JSON; it does not edit the PDF. Older output files for PDFs no longer in the input folder are not deleted or included in the new invocation's summary.

## 3. Run the sample, then expand

Run from the `techgap-final` repository directory using Python 3.10+:

```powershell
python -m pip install -r scripts/requirements-collection.txt
python scripts/extract_syllabi.py "csv/old_curriculum/S-ITWB311LA Web Development Lab.pdf" --output "data/collection_samples/syllabus"
python -B -m unittest discover -s tests -v
```

Expected sample checks, established by reading the source:

- Code `S-ITWB311LA`; title `Web Development`; type `Laboratory`; credit `One (1) Unit`.
- Prerequisites `None`; corequisites `S-ITWB311`.
- Six main CLOs.
- Midterm: CLO1/2/3/6, TLO1–3 and the additional collaboration/communication outcome text.
- Final: CLO1/2/4/5/6 and TLO4–6. CLO5/6 continue on page 6 and must be retained.
- No weekly schedule content in the saved course record.

Compare the extracted text against PDF pages 1–2 and 5–6, not just against counts. Then test a few different lecture/lab and layout examples before the full collection:

```powershell
python scripts/extract_syllabi.py "PATH_TO_SYLLABUS_FOLDER" --output "data/syllabi"
```

Review the batch summary for missing fields, failed files and unfamiliar layouts; change extraction rules only after inspecting those PDFs, then rerun. Do not assume all 100+ files share the sample template. A layout can omit text while passing simple presence checks, so source comparisons remain necessary when introducing a new template.

## 4. Sample status

**Sample passed on 2026-10-19.** See the [extracted course record](../../data/collection_samples/syllabus/S-ITWB311LA%20Web%20Development%20Lab.pdf.json) and [run summary](../../data/collection_samples/syllabus/summary.json).

The script recovered all six labelled course fields, the description, six main CLOs, both period overviews and all six TLOs. The Final table's CLO5/6 continuation on page 6 was retained. The overview wording was compared with the rendered tables on pages 2, 5 and 6; the course fields, description and main CLOs were checked against extracted source text on pages 1–2. Weekly tables were absent from the result.

Three automated source/batch checks passed: requested source values and cross-page outcomes; exclusion of weekly/unrequested content; and a batch containing two copies in separate subfolders plus a deliberately damaged PDF. The damaged file was recorded without stopping the valid files, and repeating the batch produced the same course output. These are tests of one real syllabus and batch mechanics, not accuracy measurements across the 100+ collection. Structural `ok` is not a guarantee for unseen layouts.
