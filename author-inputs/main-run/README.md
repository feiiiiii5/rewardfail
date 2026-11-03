# Main-run raw inputs (2026-10-07)

Source run: stage2/runs/main-20261007-202545.

| File | Bytes | Role |
| --- | ---: | --- |
| default/rows.jsonl | 49,088,377 | default per-row records; raw copy |
| reference/rows.jsonl | 18,475,478 | reference per-row records; raw copy |
| report.json | 1,489,776 | raw 2026-10-07 report; run_dir path sanitized |
| run.json | 6,357 | run configuration/provenance |
| guard-steps.jsonl | 20,762 | guard records |
| default/pass_spec.json, pass_done.json | small | pass configuration/completion |
| reference/pass_spec.json, pass_done.json, interrupts.json | small | reference pass configuration/completion/interrupts |

Important: the formal 2026-10-08 reanalysis is in ../reanalysis/s2_main/report.json, not this raw report. Recompute k=1/u=18 from the report and rows; do not infer it from file names alone. Child logs and the other pass rows are intentionally excluded (hundreds of MB).
