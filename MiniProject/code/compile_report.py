#!/usr/bin/env python3

from pathlib import Path
import shutil
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
report_dir = root_path / "MiniProject" / "report"
main_tex = report_dir / "main.tex"
main_pdf = report_dir / "main.pdf"
report_pdf = report_dir / "report.pdf"


def require_command(command: str) -> str:
    command_path = shutil.which(command)
    if command_path is not None:
        return command_path
    raise FileNotFoundError(
        f"Required LaTeX command not found: {command}. "
        "Please install MiKTeX or TeX Live, or add the LaTeX bin directory to PATH."
    )


def run_command(command: list[str]) -> None:
    print("Running:", " ".join(command))
    subprocess.run(command, check=True, cwd=report_dir)


def cleanup_report_dir() -> None:
    keep_entries = {"fig", "main.tex", "references.bib", "report.pdf"}
    for path in report_dir.iterdir():
        if path.name in keep_entries:
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def ensure_wordcount_fallback() -> None:
    # Keep compilation robust when texcount is unavailable.
    wordcount_file = report_dir / "wordcount.txt"
    if not wordcount_file.exists():
        wordcount_file.write_text("0\n", encoding="utf-8")


def rename_output_pdf() -> None:
    if not main_pdf.exists():
        raise FileNotFoundError(f"Expected compiled PDF not found: {main_pdf}")
    if report_pdf.exists():
        report_pdf.unlink()
    main_pdf.rename(report_pdf)


def compile_with_pdflatex() -> None:
    pdflatex = require_command("pdflatex")
    bibtex = require_command("bibtex")

    pdflatex_cmd = [
        pdflatex,
        "-interaction=nonstopmode",
        "-shell-escape",
        str(main_tex.name),
    ]

    run_command(pdflatex_cmd)
    run_command([bibtex, main_tex.stem])
    run_command(pdflatex_cmd)
    run_command(pdflatex_cmd)


def main() -> None:
    if not main_tex.exists():
        raise FileNotFoundError(f"Could not find LaTeX entry file: {main_tex}")

    print(f"Report directory: {report_dir}")
    print(f"Compiling: {main_tex.name}")
    ensure_wordcount_fallback()
    compile_with_pdflatex()

    rename_output_pdf()
    cleanup_report_dir()
    print(f"Compilation completed: {report_pdf}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
    except FileNotFoundError as exc:
        print(exc)
        sys.exit(1)
