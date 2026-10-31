# Curated career-role list — DRAFT for approval

**Status:** Agent draft, 2026-10-27. Not a decision until the user approves it. Fills the open "curated career-role list" input in [PLANNED_DATA_FLOW.md](PLANNED_DATA_FLOW.md) §1 and §6.

**Method:** Broad grouping of original employer titles from the 497-ID saved frame. Only the 356 employment postings with provisional technically assessable text and at least one track/Shared-core link were grouped. Titles were matched by simple keyword rules in the order shown (first match wins). Search queries, ESCO and seniority were not used. Sources: [four-track assessment CSV](../../data/job_collections/jobstreet-2026-10-four-track-offline-audit-20261024/four_track_saved_posting_assessment_2026-10-24.csv) and [Game campaign CSV](../../data/job_collections/jobstreet-2026-10-game-four-query-proposal/four_query_game_campaign_assessment_2026-10-24.csv).

**Limits:** Counts are title-keyword approximations over automated provisional labels. They show which roles are sparse; they are not demand figures. The pipeline will later link each posting to a role from its title and, where the title is generic, its duties. A role can stay selectable with zero assessable postings, but then it has no numeric score.

| # | Proposed role | Approx. postings | Main tracks seen | Example employer titles |
| ---: | --- | ---: | --- | --- |
| 1 | AI / Machine Learning Engineer | 48 | IS | AI Engineer; AI/ML Engineer; Machine Learning Engineer; Agentic AI Engineer |
| 2 | Data Engineer | 29 | IS | Data Engineer; ETL Data Engineer; Senior Databricks & Azure Data Engineer |
| 3 | Data Scientist | 9 | IS | Data Scientist; Full Stack Data Scientist |
| 4 | Data Analyst | 10 | IS / Shared | Data Analyst; Data Analytics Engineer |
| 5 | Game Developer | 9 | GD | Unity Game Developer; Video Game Developer; Mobile Game Programmer |
| 6 | Game Designer | 7 | GD | Game Designer; Narrative Game Designer; Game UI Designer |
| 7 | Game QA Tester | 3 | GD | Video Game Tester; Associate Test Lead - Video Game QA |
| 8 | Network Engineer / Administrator (incl. NOC) | 38 | NT | Network Engineer; Network Administrator; NOC Engineer |
| 9 | Systems Administrator | 14 | NT | Systems Administrator; System Administrator – Wintel & Network |
| 10 | Cybersecurity / SOC Analyst | 23 | NT | SOC Analyst; Cybersecurity Analyst; Security Operations Center Analyst |
| 11 | Full Stack Developer | 31 | WD | Full Stack Developer; Full Stack Engineer |
| 12 | Frontend Developer | 9 | WD | Frontend Developer; Front-End Developer - React + TypeScript |
| 13 | Backend Developer | 6 | WD | Backend Developer (Go); Lead Backend Developer |
| 14 | Web Developer | 8 | WD | Web Developer; Junior Web Developer |
| 15 | Mobile Developer | 2 | WD / Shared | Mobile Developer (Android); Mobile App Programmer |
| 16 | Software Developer / Engineer (general) | 57 | Shared / WD | Software Developer; Software Engineer; Application Developer; Programmer |
| 17 | QA / Software Tester | 38 | Shared | QA Engineer; Software Tester; QA Automation Engineer |
| 18 | IT Support / Service Desk | 13 | Shared | IT Helpdesk Support Engineer; Service Desk Analyst; Technical Support Engineer |
| 19 | UI/UX / Web Designer | 2 | Shared | UI/UX Designer - Figma; Web Designer |

## Questions for approval

1. Merge **Frontend, Backend and Web Developer** into one Web Developer role, or keep them separate? Backend (6) and Frontend (9) are sparse.
2. Keep **Mobile Developer** (2) and **UI/UX / Web Designer** (2) as roles, or drop them until more postings exist?
3. Keep **NOC** inside Network Engineer / Administrator, or make NOC its own role?
4. Keep **IT Support / Service Desk** as a student-facing role? None of its postings link to a specific track.
5. Game roles are sparse (19 postings in total). Keep all three, or combine them into one Game Development role for now?
