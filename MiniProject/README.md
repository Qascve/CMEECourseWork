# MiniProject

Dir contains things of MiniProject CMEECourseWork.

## Structure

- **code:** All analysis and pipeline scripts.
- **data:** Input datasets and intermediate processed datasets.
- **result:** Model fitting results, metrics tables, and plots.
- **report:** LaTeX source files and final PDF report.

## Prerequisites

### Python environment

- Python 3.9+ (recommended: 3.10 or newer)
- Install required Python packages:

```bash
python -m pip install numpy pandas matplotlib lmfit
```

### LaTeX environment (for report compilation)

- `pdflatex` and `bibtex` available in `PATH`
- TeX distribution: TeX Live or MiKTeX
- Optional: `perl` (used only when `texcount` is available)

Linux quick check:

```bash
which pdflatex
which bibtex
```

Windows quick check:

```powershell
where pdflatex
where bibtex
```

## Usage

### Run full pipeline

Purpose: run all data processing, model fitting, summary plotting, and report compilation in sequence.

```bash
python MiniProject/code/run_MiniProject.py
```

Notes:
- Pipeline order is fixed inside `run_MiniProject.py`.
- The script checks required Python packages (`numpy`, `pandas`, `matplotlib`, `lmfit`) before running.

### Run scripts one by one

**explore_dataset.py**  
Purpose: inspect raw growth dataset, summarize species/medium/temperature coverage, export filtered target dataset (`Tetraselmis tetrahele`, `ESAW`, 8/16/25 C), and save an exploratory summary plot.

```bash
python MiniProject/code/explore_dataset.py
```

**create_log_dataset.py**  
Purpose: transform `PopBio` to `log_PopBio`, filter invalid values, and create logged dataset for model fitting.

```bash
python MiniProject/code/create_log_dataset.py
```

**logistic_fit.py**  
Purpose: fit logistic model at each temperature with multi start optimization; save per-temperature and combined plots, plus fit metrics table.

```bash
python MiniProject/code/logistic_fit.py
```

**baranyi_fit.py**  
Purpose: fit Baranyi model at each temperature with multi start optimization; save plots and metrics table.

```bash
python MiniProject/code/baranyi_fit.py
```

**three_phase_linear_fit.py**  
Purpose: fit three-phase linear growth model at each temperature; save plots and metrics table.

```bash
python MiniProject/code/three_phase_linear_fit.py
```

**model_comparison_summary.py**  
Purpose: compare model performance at 8/16/25 C, generate model comparison plots, and save merged metrics table.

```bash
python MiniProject/code/model_comparison_summary.py
```

**compile_report.py**  
Purpose: compile LaTeX report using:
`main.pdf` will be rename to `report.pdf` and clean temporary files in report directory.

```bash
python MiniProject/code/compile_report.py
```

## Main inputs and outputs

### Key inputs

- `MiniProject/data/logistic_growth_data.csv` (raw data)
- `MiniProject/report/main.tex` and `MiniProject/report/references.bib` (report source)

### Key generated files

- `MiniProject/data/tetraselmis_tetrahele.csv`
- `MiniProject/data/tetraselmis_tetrahele_log.csv`
- `MiniProject/result/logistic_fit/fit_metrics_by_temp.csv`
- `MiniProject/result/baranyi_fit/fit_metrics_by_temp.csv`
- `MiniProject/result/three_phase_linear_fit/fit_metrics_by_temp.csv`
- `MiniProject/result/model_comparison_summary/model_metrics_all_temps.csv`
- `MiniProject/report/report.pdf`

