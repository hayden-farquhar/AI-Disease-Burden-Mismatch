# Medical AI Research–Disease Burden Mismatch: Replication Code

Replication code and data for:

> Farquhar, H. (2026). Medical artificial intelligence research is misaligned with global disease burden: a bibliometric analysis of 197,844 publications. *Scientometrics* [submitted].

## Overview

This repository contains the code required to replicate all analyses, figures, and tables presented in the paper. It maps 197,844 medical AI publications (2015–2025) from OpenAlex to 115 Global Burden of Disease 2023 Level 3 causes and computes a Research Attention Index (RAI) quantifying each disease's publication share relative to its DALY share.

## Requirements

- Python 3.10+
- Dependencies: see `requirements.txt`

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Data

### Included in this repository
- `src/collect/gbd_causes.py` — GBD Level 3 cause-term dictionary (124 diseases, 424 search terms)
- `src/collect/gbd_name_mapping.py` — Mapping between our dictionary names and official GBD 2023 names
- `data/gbd/` — Placeholder for GBD DALY data (must be downloaded separately due to IHME terms of use)

### Data to download
1. **GBD 2023 DALY data**: Download from https://vizhub.healthdata.org/gbd-results/ with settings: Measure = DALYs, Metric = Number, Location = Global, Year = 2021, Age = All ages, Sex = Both, Cause = Level 3. Save as `data/gbd/gbd_2023_global_dalys_number.csv`.
2. **GBD 2023 SDI data**: Same settings but Location = by SDI quintile (Low, Low-middle, Middle, High-middle, High SDI). Save as `data/gbd/gbd_2023_sdi_dalys_number.csv`.

OpenAlex publication data is collected via API at runtime (no download required).

## Replication

Run the full pipeline:

```bash
python -m src.pipeline
```

This will:
1. Collect medical AI publications from OpenAlex (cached after first run)
2. Map publications to GBD diseases
3. Compute the Research Attention Index
4. Run all analyses (temporal, equity, regression, corrective modelling)
5. Generate all figures
6. Save all output data to `outputs/`

Individual steps can also be run separately — see `src/pipeline.py` for details.

### Expected runtime
- OpenAlex collection: ~2–3 hours (first run; rate-limited to ~200 requests/minute)
- Analysis and figures: ~5 minutes

## Repository structure

```
repository/
├── README.md
├── requirements.txt
├── LICENSE
├── src/
│   ├── __init__.py
│   ├── pipeline.py              # Full replication pipeline
│   ├── collect/
│   │   ├── __init__.py
│   │   ├── openalex_client.py   # OpenAlex API client
│   │   ├── gbd_loader.py        # GBD data loader
│   │   ├── gbd_causes.py        # Disease-term dictionary
│   │   ├── gbd_name_mapping.py  # Name reconciliation
│   │   └── disease_mapper.py    # Publication-to-disease mapping
│   ├── analyse/
│   │   ├── __init__.py
│   │   ├── attention_index.py   # RAI computation
│   │   └── temporal_trends.py   # Temporal analysis
│   └── visualise/
│       ├── __init__.py
│       ├── style.py             # Plot styling
│       └── generate_figures.py  # All publication figures
├── data/
│   └── gbd/                    # GBD data (download separately)
└── outputs/                    # Generated data and figures
```

## Citation

If you use this code, please cite:

```bibtex
@article{farquhar2026mismatch,
  title={Medical artificial intelligence research is misaligned with global disease burden: a bibliometric analysis of 197,844 publications},
  author={Farquhar, Hayden},
  journal={Scientometrics},
  year={2026},
  note={Submitted}
}
```

## Licence

MIT License. See `LICENSE`.

## Data sources

- **OpenAlex**: Priem, J., Piwowar, H., & Orr, R. (2022). OpenAlex: A fully-open index of scholarly works. arXiv:2205.01833. CC0 licence.
- **GBD 2023**: GBD 2023 Collaborators (2025). The Lancet, 406(10513), 1873–1922. IHME free access with registration.
