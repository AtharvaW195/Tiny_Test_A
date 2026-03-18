import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def _resolve_dataset_path(path: Path) -> Path:
    path = path.expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Dataset path not found: {path}")
    # Allow passing the dataset root (contains a `data/` folder)
    data_subdir = path / "data"
    if data_subdir.is_dir():
        return data_subdir
    return path


def _assert_has_images(data_path: Path) -> None:
    has_jpg = any(data_path.rglob("*.jpg"))
    if not has_jpg:
        raise ValueError(f"No .jpg images found under: {data_path}")


def _ensure_kernel_spec(*, kernel_name: str, python_executable: str, jupyter_path_dir: Path) -> None:
    kernels_dir = jupyter_path_dir / "kernels" / kernel_name
    kernels_dir.mkdir(parents=True, exist_ok=True)

    kernel_json = {
        "argv": [
            python_executable,
            "-m",
            "ipykernel_launcher",
            "-f",
            "{connection_file}",
        ],
        "display_name": f"{kernel_name}",
        "language": "python",
    }

    (kernels_dir / "kernel.json").write_text(json.dumps(kernel_json, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the existing notebook-based pipeline.")
    parser.add_argument(
        "--notebook",
        default="setup_configuration.ipynb",
        help="Notebook entry point (default: setup_configuration.ipynb).",
    )
    parser.add_argument(
        "--data-path",
        default=None,
        help="Dataset path (either the dataset root or the `data/` folder).",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: notebook's OUTPUT_DIR).",
    )
    parser.add_argument(
        "--executed-notebook",
        default=None,
        help="Where to write the executed notebook (default: <output-dir>/executed_<notebook>.ipynb).",
    )
    parser.add_argument(
        "--kernel",
        default="tiny_test_a_venv",
        help="Kernel name to use for execution (default: tiny_test_a_venv).",
    )
    args = parser.parse_args()

    notebook_path = Path(args.notebook).expanduser().resolve()
    if not notebook_path.exists():
        raise FileNotFoundError(f"Notebook not found: {notebook_path}")

    env = os.environ.copy()

    if args.data_path:
        data_path = _resolve_dataset_path(Path(args.data_path))
        _assert_has_images(data_path)
        env["PIPELINE_DATA_PATH"] = str(data_path)

    executed_notebook_path: Path | None = None
    if args.executed_notebook:
        executed_notebook_path = Path(args.executed_notebook).expanduser().resolve()
    elif args.output_dir:
        out_dir = Path(args.output_dir).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        executed_notebook_path = out_dir / f"executed_{notebook_path.name}"
    else:
        executed_notebook_path = (Path.cwd() / f"executed_{notebook_path.name}").resolve()

    if args.output_dir:
        out_dir = Path(args.output_dir).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        env["PIPELINE_OUTPUT_DIR"] = str(out_dir)

    # Helps reduce CUDA allocator fragmentation on long runs.
    env.setdefault(
        "PYTORCH_CUDA_ALLOC_CONF",
        "expandable_segments:True,max_split_size_mb:128,garbage_collection_threshold:0.8",
    )

    # Force execution using the *current* Python environment (avoids picking up a different
    # system/conda kernel that may not have torch installed).
    try:
        __import__("ipykernel")  # noqa: S404
    except Exception as e:
        raise RuntimeError(
            "ipykernel is required to execute the notebook from this environment. "
            "Install it in your venv (e.g. `pip install ipykernel`)."
        ) from e

    jupyter_path_dir = executed_notebook_path.parent / ".jupyter_path"
    _ensure_kernel_spec(
        kernel_name=args.kernel,
        python_executable=sys.executable,
        jupyter_path_dir=jupyter_path_dir,
    )
    env["JUPYTER_PATH"] = os.pathsep.join([str(jupyter_path_dir), env.get("JUPYTER_PATH", "")]).strip(os.pathsep)

    cmd = [
        sys.executable,
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        "--ExecutePreprocessor.kernel_name",
        args.kernel,
        str(notebook_path),
        "--output",
        str(executed_notebook_path),
    ]

    try:
        subprocess.run(cmd, check=True, env=env)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Pipeline execution failed (nbconvert exit code {e.returncode}).") from e

    print(f"✅ Executed notebook saved to: {executed_notebook_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
