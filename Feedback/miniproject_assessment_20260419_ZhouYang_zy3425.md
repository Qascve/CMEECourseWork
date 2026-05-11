# MiniProject Assessment for Zhou Yang

## Computing

### A1 — Project Organisation

The project is easy to navigate at first glance: `code/`, `data/`, `report/`, and `result/` are all present, and the README gives Python and LaTeX prerequisites together with script-by-script usage. The main organisational drag is that the expected rubric directory is `results/`, but the submission uses `result/`, and a large number of generated PDFs and CSVs are committed under that folder and under `report/fig`, which weakens the clean-regeneration standard expected for reproducible coursework. The README also stops short of explaining what each package is for, so a reader can install dependencies but gets less help understanding why `numpy`, `pandas`, `matplotlib`, and `lmfit` are each needed in the workflow.

### A2 — Single-Script Reproducibility

#### Workflow & Solution Quality

`run_MiniProject.py` starts by checking dependencies and then stops immediately after printing that `lmfit` is missing in the grading environment. The script itself is a real orchestrator: it lists seven ordered stages from `explore_dataset.py` through `compile_report.py`, runs each with `subprocess.run(..., check=True)`, and uses project-root-relative paths, which is the right structure for end-to-end reproducibility. The main weakness is that the dependency preflight returns successfully instead of failing loudly, so the run log reports exit code 0 even though no analysis stages were executed and no new outputs were generated. A stronger submission would make missing dependencies terminate with a non-zero exit status, write a short run log, and document whether each non-core dependency is truly necessary for this submission; in particular, it is worth asking whether `lmfit` is essential here or whether a lighter standard stack could reduce reproducibility friction.

### A3 — Code Quality & Style

#### Script-level Technical Feedback

The codebase is substantial and strongly modularised: 2167 lines of Python are split across eight scripts, with 103 function definitions in total, and the larger fitting files such as `code/three_phase_linear_fit.py` and `code/baranyi_fit.py` are broken into sensible helpers like `initial_theta`, `build_fixed_initial_thetas`, `fit_with_fixed_starts`, and `compute_fit_metrics`. `code/model_comparison_summary.py` also shows good separation of concerns through functions such as `fit_models_at_temperature` and `build_metrics_summary_table`, which makes the analysis easier to inspect and reuse than a single monolithic notebook-style script. The main style weakness is documentation: comment density is only 0.006, with 14 comment lines across the whole codebase, so many implementation choices have to be inferred from function names alone rather than being explained inline. A next step would be to add concise docstrings and targeted comments around non-obvious parts such as parameter transformations, start-value heuristics, and the model-selection logic in `fit_with_fixed_starts`.

### A4 — Model Fitting & Statistical Analysis

#### NLLS

The fitting code goes well beyond a minimal attempt: `code/logistic_fit.py`, `code/baranyi_fit.py`, and `code/three_phase_linear_fit.py` each fit one model separately across 8, 16, and 25 °C using `lmfit.minimize(..., method="leastsq")`, with 16 fixed-start candidates per model and AIC used to choose the retained fit. Starting values are not arbitrary; `initial_theta` and `build_fixed_initial_thetas` in both `baranyi_fit.py` and `three_phase_linear_fit.py` derive guesses from the observed range and timing of the data, and convergence failures are handled explicitly with `try/except` inside the multi-start loops so failed starts do not crash the whole fitting stage. The analysis also computes and exports `R2`, `RMSE`, `MAE`, `AIC`, and `BIC`, and the report presents coherent cross-model comparison for Logistic, Baranyi, and three-phase linear fits. Future work could make the NLLS setup easier to defend by stating the start-value heuristics and parameter bounds explicitly in the report and by logging how many starts failed for each temperature alongside the successful fit summaries.

### A5 — Version Control & Workflow Discipline

The Git history shows sustained development rather than a last-minute dump: there are 15 MiniProject commits, with a clear progression from `explore dataset` to model fitting, workflow assembly, and LaTeX/report fixes. Commit messages are usually short but still informative enough to reconstruct the project’s evolution, although the history would be cleaner with fewer committed generated PDFs and with more descriptive messages for final polishing commits. Future submissions would benefit from keeping outputs out of version control and using commit messages that record the analytical reason for a change, not just the file action.

## Report

### B1 — Report Format & Presentation

The report is readable and sensibly sized at about 2867 words, includes an abstract, uses 1.5 spacing, and contains 5 display items with matching captions, which sits comfortably in the expected range. The main formatting issue is that the document uses `\documentclass[11pt,onecolumn,draftclsnofoot]{IEEEtran}` rather than the required LaTeX `article` class, and line numbering is missing because `lineno` is not used. The title page does include author, affiliation, and word count in the body of the `.tex`, but the formal front-matter setup is less conventional than the rubric expects. 

### B2 — Introduction & Objectives

The Introduction gives a biologically relevant opening around population growth, lag phases, and model choice, and it does move toward a concrete comparison among Logistic, Baranyi, and three-phase linear models for `Tetraselmis tetrahele` across 8, 16, and 25 °C. The weaker part is the course-specific framing: the required grounding in temperature-dependent single-population metabolism/growth from the relevant MQB chapters is not established, chapter references are absent, and the biological objective is not clearly separated from the methodological objective of comparing models. The hypothesis is present, but the narrative would be stronger if it linked temperature, growth physiology, and model expectations more explicitly before introducing the fitting exercise.

### B3 — Methods (including Computing Tools)

The Methods section covers data restriction, log transformation, the three candidate models, multi-start fitting, and the comparison metrics `R^2`, RMSE, AIC, and BIC, so a reader can follow the broad analytical workflow. The Computing Tools subsection is present and does justify the use of Python with `pandas`, `numpy`, `matplotlib`, `lmfit`, and `pathlib`, which is a good match to the rubric. The main omission is mathematical specificity: the report describes the models verbally but does not present equations, and it also leaves out some fitting details that matter for reproducibility, such as how starting values were generated and how failed starts were handled. A stronger methods write-up would include the explicit model equations and a short account of the multi-start NLLS procedure used in the fitting scripts.

### B4 — Results & Display Items

The Results section is well populated, with 4 figures and 1 table, and the table of `R^2`, RMSE, AIC, and BIC across temperatures gives the reader a clear model-comparison summary. The section also follows the temperature structure consistently, moving through 8, 16, and 25 °C in a way that matches the stated objectives. Some interpretation leaks into the prose through statements about ecological meaning and phase visibility, so the boundary between factual reporting and discussion is not always clean. The display items themselves are useful and appropriately captioned, but future work could make the captions more informative by stating the take-home message directly rather than only naming what is shown.

### B5 — Discussion, Conclusions & Abstract

The Discussion returns to the main finding that the three-phase linear model performs best at lower and intermediate temperatures and interprets that in terms of lag-phase visibility and biological phase structure, which gives the project a clear take-home message. There is also meaningful engagement with advanced methods: the later discussion paragraph considers likelihood-based approaches, neural networks, and deep learning, and connects them to overfitting risk, interpretability, and limited data scale rather than mentioning them only in passing. Two issues hold this back from the top band: the report contains a duplicated `Discussion` section heading, and the abstract is somewhat short at about 154 words and does not fully capture caveats or methodological detail in a self-contained way. A stronger final version would integrate the advanced-methods paragraph more tightly with the biological question and sharpen the abstract so that background, methods, key numerical findings, and conclusion all stand on their own.

## Summary

Final classification (student-facing):

- Part A (Computing): Distinction
- Part B (Report): Distinction
- Overall: Distinction
