#!/usr/bin/env python3

from pathlib import Path
import os
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
report_dir_rel = Path("MiniProject") / "report"
report_dir = root_path / report_dir_rel
main_tex = report_dir / "main.tex"
main_pdf = report_dir / "main.pdf"
report_pdf = report_dir / "report.pdf"
texcount_wrapper = report_dir / "texcount.cmd"


def require_command(command: str) -> str:
    command_path = shutil.which(command)
    if command_path is not None:
        return command_path
    raise FileNotFoundError(
        f"Required LaTeX command not found: {command}. "
        "Please install MiKTeX or TeX Live, or add the LaTeX bin directory to PATH."
    )


def run_command(command: list[str], *, stream_output: bool = False) -> None:
    print("Running:", " ".join(command))
    env = os.environ.copy()
    env["PATH"] = str(report_dir) + os.pathsep + env.get("PATH", "")
    if stream_output:
        subprocess.run(command, check=True, cwd=report_dir, env=env)
        return

    completed = subprocess.run(
        command,
        check=False,
        cwd=report_dir,
        env=env,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        if completed.stdout:
            print(completed.stdout)
        if completed.stderr:
            print(completed.stderr)
        raise subprocess.CalledProcessError(
            completed.returncode,
            command,
            output=completed.stdout,
            stderr=completed.stderr,
        )


def print_final_latex_diagnostics() -> None:
    log_file = report_dir / "main.log"
    if not log_file.exists():
        return

    warning_lines: list[str] = []
    for line in log_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "LaTeX Warning:" in line or "Package " in line and " Warning:" in line:
            warning_lines.append(line.strip())

    if not warning_lines:
        print("Final pdflatex diagnostics: no warnings in main.log")
        return

    print("Final pdflatex diagnostics (from last pass):")
    for line in warning_lines:
        print(line)


def cleanup_report_dir() -> None:
    keep_entries = {"fig", "main.tex", "references.bib", "report.pdf"}
    for path in report_dir.iterdir():
        if path.name in keep_entries:
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def setup_texcount_wrapper() -> None:
    perl = shutil.which("perl")
    if perl is None:
        return

    base_dirs = [os.environ.get("PROGRAMFILES"), os.environ.get("PROGRAMFILES(X86)")]
    candidates = [
        Path(base_dir) / "MiKTeX" / "scripts" / "texcount" / "texcount.pl"
        for base_dir in base_dirs
        if base_dir
    ]

    texcount_pl = next((p for p in candidates if p.exists()), None)
    if texcount_pl is None:
        return

    wrapper_content = (
        "@echo off\r\n"
        f"\"{perl}\" \"{texcount_pl}\" %*\r\n"
    )
    texcount_wrapper.write_text(wrapper_content, encoding="ascii")


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

    run_command(pdflatex_cmd, stream_output=False)
    run_command([bibtex, main_tex.stem], stream_output=False)
    run_command(pdflatex_cmd, stream_output=False)
    run_command(pdflatex_cmd, stream_output=False)
    print_final_latex_diagnostics()


def main() -> None:
    if not main_tex.exists():
        raise FileNotFoundError(f"Could not find LaTeX entry file: {main_tex}")

    print(f"Report directory: {report_dir}")
    print(f"Compiling: {main_tex.name}")
    setup_texcount_wrapper()
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
