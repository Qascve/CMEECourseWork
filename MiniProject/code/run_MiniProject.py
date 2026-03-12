#!/usr/bin/env python3

from pathlib import Path
import importlib.util
import subprocess
import sys


def find_root(start_path: Path) -> Path:
    current = start_path.resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if (candidate / ".gitignore").exists():
            return candidate
    raise FileNotFoundError("Could not find project root via .gitignore")


root_path = find_root(Path(__file__))
code_dir = root_path / "MiniProject" / "code"

# module name -> pip package name
required_packages = {
    "numpy": "numpy",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "lmfit": "lmfit",
}

pipeline_steps = [
    ("Explore dataset", code_dir / "explore_dataset.py"),
    ("Create logged dataset", code_dir / "create_log_dataset.py"),
    ("Run logistic model fit", code_dir / "logistic_fit.py"),
    ("Run Baranyi model fit", code_dir / "baranyi_fit.py"),
    ("Run three-phase linear model fit", code_dir / "three_phase_linear_fit.py"),
    ("Summarize model comparison", code_dir / "model_comparison_summary.py"),
    ("Compile LaTeX report", code_dir / "compile_report.py"),
]


def check_required_packages() -> bool:
    missing = [
        pip_name
        for module_name, pip_name in required_packages.items()
        if importlib.util.find_spec(module_name) is None
    ]
    if not missing:
        return True

    print("Missing required Python packages:")
    for package_name in missing:
        print(f"  - {package_name}")
    print("\nPlease install them and rerun:")
    print(f"{sys.executable} -m pip install {' '.join(missing)}")
    return False


def run_step(step_name: str, script_path: Path) -> None:
    print(f"\n=== {step_name} ===")
    print(f"Script: {script_path}")
    subprocess.run(
        [sys.executable, str(script_path)],
        check=True,
        cwd=root_path,
    )


def main() -> None:
    if not check_required_packages():
        return

    print(f"Project root: {root_path}")
    print("Running MiniProject pipeline:")
    for idx, (step_name, script_path) in enumerate(pipeline_steps, start=1):
        print(f"{idx}. {step_name}")

    for step_name, script_path in pipeline_steps:
        run_step(step_name, script_path)

    print("\nMiniProject pipeline completed successfully.")


if __name__ == "__main__":
    main()
