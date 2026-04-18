from __future__ import annotations

from pathlib import Path
import sys


OUTPUT_DIR = Path(__file__).resolve().parent / "graph_images"


def _draw_graph_png(graph_obj) -> bytes:
    errors: list[str] = []

    try:
        return graph_obj.draw_mermaid_png()
    except Exception as exc:
        errors.append(f"default renderer failed: {exc}")

    try:
        from langchain_core.runnables.graph import MermaidDrawMethod
    except Exception as exc:
        errors.append(f"MermaidDrawMethod import failed: {exc}")
    else:
        for draw_method in (MermaidDrawMethod.API, MermaidDrawMethod.PYPPETEER):
            try:
                return graph_obj.draw_mermaid_png(draw_method=draw_method)
            except Exception as exc:
                errors.append(f"{draw_method} failed: {exc}")

    raise RuntimeError(" | ".join(errors))


def export_graph_images(output_dir: Path = OUTPUT_DIR) -> list[tuple[str, Path, Path]]:
    from graph.graph import build_auth_app, build_guest_app

    output_dir.mkdir(parents=True, exist_ok=True)

    apps = {
        "guest": build_guest_app(),
        "auth": build_auth_app(),
    }
    exported: list[tuple[str, Path, Path]] = []

    for name, app in apps.items():
        graph_obj = app.get_graph()

        mermaid_path = output_dir / f"{name}_graph.mmd"
        mermaid_path.write_text(graph_obj.draw_mermaid(), encoding="utf-8")

        png_path = output_dir / f"{name}_graph.png"
        png_path.write_bytes(_draw_graph_png(graph_obj))

        exported.append((name, png_path, mermaid_path))

    return exported


def main() -> int:
    try:
        exported = export_graph_images()
    except ModuleNotFoundError as exc:
        missing = exc.name or str(exc)
        print(f"Missing dependency: {missing}", file=sys.stderr)
        print("Install the project dependencies first, then rerun graph_test.py.", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Failed to export graph images: {exc}", file=sys.stderr)
        return 1

    for name, png_path, mermaid_path in exported:
        print(f"{name} graph image: {png_path}")
        print(f"{name} graph mermaid: {mermaid_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
