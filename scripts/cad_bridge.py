"""Structured CAD jobs. Validation is portable; execution requires Windows + pywin32."""
import argparse
import json
import math
import os
from pathlib import Path
import re
import shutil
import sys
import uuid

UNITS = {"mm": 4, "cm": 5, "m": 6, "inch": 1}


def point(value):
    if not isinstance(value, list) or len(value) != 3 or any(
        type(x) not in (int, float) or not math.isfinite(x) for x in value
    ):
        raise ValueError("Point must contain three finite numbers")
    return value


def validate(job):
    if not isinstance(job, dict) or set(job) != {"units", "source", "operations"}:
        raise ValueError("Expected units, source, operations only")
    if job["units"] not in UNITS:
        raise ValueError("Explicit units required: mm/cm/m/inch")
    source = job["source"]
    if source is not None and (not isinstance(source, str) or not re.fullmatch(
        r"[A-Za-z0-9_-]{1,100}\.dwg", source, re.I
    )):
        raise ValueError("source must be null or a simple ASCII .dwg filename")
    ops = job["operations"]
    if not isinstance(ops, list) or not 1 <= len(ops) <= 1000:
        raise ValueError("Expected 1..1000 operations")
    for op in ops:
        if not isinstance(op, dict):
            raise ValueError("Operation must be an object")
        kind = op.get("type")
        keys = {"line": {"type", "start", "end"},
                "circle": {"type", "center", "radius"},
                "move": {"type", "handle", "offset"}}
        if kind not in keys or set(op) != keys[kind]:
            raise ValueError("Unsupported operation or fields")
        if kind == "line":
            if point(op["start"]) == point(op["end"]):
                raise ValueError("Zero-length line")
        elif kind == "circle":
            point(op["center"])
            r = op["radius"]
            if type(r) not in (int, float) or not math.isfinite(r) or r <= 0:
                raise ValueError("Radius must be positive and finite")
        else:
            point(op["offset"])
            if source is None or not isinstance(op["handle"], str) or not re.fullmatch(r"[0-9A-Fa-f]{1,16}", op["handle"]):
                raise ValueError("Move requires a source drawing and object handle")
    return job


def source_path(root, name):
    base = (root / "inputs").resolve()
    source = (base / name).resolve()
    if source.parent != base or not source.is_file():
        raise ValueError("Source must be an existing file inside CAD_HOME/inputs")
    return source


def execute(job, root, progid="AutoCAD.Application"):
    validate(job)
    if sys.platform != "win32":
        raise RuntimeError("CAD execution requires Windows")
    import pythoncom
    import win32com.client
    source = source_path(root, job["source"]) if job["source"] else None
    folder = root / "outputs" / uuid.uuid4().hex
    folder.mkdir(parents=True, exist_ok=False)
    output = folder / "result.dwg"
    # Only open an isolated copy. Never open or save the original via AutoCAD.
    if source:
        shutil.copy2(source, output)
    pythoncom.CoInitialize()
    doc = None
    try:
        app = win32com.client.DispatchEx(progid)
        app.Visible = True
        # AutoCAD 2027 belongs to the R25.2 release; reject another registered release.
        if not str(app.Version).startswith("25.2"):
            raise RuntimeError("Expected AutoCAD 2027 (25.2); check COM registration")
        doc = app.Documents.Open(str(output)) if source else app.Documents.Add()
        actual_units = int(doc.GetVariable("INSUNITS"))
        if source and actual_units != UNITS[job["units"]]:
            raise ValueError("Source INSUNITS does not match declared units; inspect drawing first")
        doc.SetVariable("INSUNITS", UNITS[job["units"]])
        # Missing or relative external assets cannot be safely copied as a standalone DWG.
        if source:
            if any(bool(b.IsXRef) for b in doc.Blocks):
                raise ValueError("Xrefs require a separately reviewed packaged drawing")
            if any(str(e.ObjectName) in {"AcDbRasterImage", "AcDbPdfReference", "AcDbDgnReference", "AcDbDwfReference"}
                   for b in doc.Blocks for e in b):
                raise ValueError("External image/underlay references require manual packaging")
        def variant(p):
            return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, p)
        handles = []
        for op in job["operations"]:
            if op["type"] == "line":
                entity = doc.ModelSpace.AddLine(variant(op["start"]), variant(op["end"]))
            elif op["type"] == "circle":
                entity = doc.ModelSpace.AddCircle(variant(op["center"]), op["radius"])
            else:
                entity = doc.HandleToObject(op["handle"])
                entity.Move(variant([0, 0, 0]), variant(op["offset"]))
            handles.append(str(entity.Handle))
        doc.Regen(1)
        if source:
            doc.Save()
        else:
            doc.SaveAs(str(output))
        doc.Close(False)
        doc = None
        if not output.is_file() or output.stat().st_size == 0:
            raise RuntimeError("AutoCAD did not produce a DWG")
        report = {"status": "saved", "units": job["units"], "handles": handles,
                  "autocad_version": str(app.Version), "drawing": "result.dwg",
                  "visual_review": "required", "job": job}
        (folder / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return folder
    except Exception:
        # Partial output must not be mistaken for a completed job.
        (folder / "FAILED.txt").write_text("Job failed; do not use any drawing in this folder.", encoding="utf-8")
        raise
    finally:
        if doc is not None:
            try:
                doc.Close(False)
            except Exception:
                pass
        pythoncom.CoUninitialize()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    raw = args.job.read_text(encoding="utf-8-sig") if args.job else os.environ["CAD_JOB_JSON"]
    job = validate(json.loads(raw))
    if args.validate_only:
        print("Job valid; AutoCAD has not been invoked")
        return
    root = Path(os.environ["CAD_HOME"]).resolve()
    folder = execute(job, root, os.environ.get("CAD_PROGID", "AutoCAD.Application"))
    print(f"Saved: {folder}")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as stream:
            stream.write(f"folder={folder}\n")


if __name__ == "__main__":
    main()
