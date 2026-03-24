
#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os
from dataclasses import asdict, dataclass
import numpy as np
import scipy.ndimage as ndi
import trimesh

@dataclass
class MeshSummary:
    vertices: int
    faces: int
    watertight: bool
    winding_consistent: bool
    euler_number: int
    components: int
    bounds_min: list[float]
    bounds_max: list[float]
    extents: list[float]

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def mesh_summary(mesh: trimesh.Trimesh) -> MeshSummary:
    bounds = mesh.bounds
    return MeshSummary(
        vertices=int(len(mesh.vertices)),
        faces=int(len(mesh.faces)),
        watertight=bool(mesh.is_watertight),
        winding_consistent=bool(mesh.is_winding_consistent),
        euler_number=int(mesh.euler_number),
        components=int(len(mesh.split(only_watertight=False))),
        bounds_min=[float(x) for x in bounds[0]],
        bounds_max=[float(x) for x in bounds[1]],
        extents=[float(x) for x in mesh.extents],
    )

def repair_mesh(input_path: str, output_path: str, summary_path: str | None = None, pitch: float = 0.25, min_component_faces: int = 100) -> dict:
    mesh = trimesh.load_mesh(input_path, force="mesh")
    original_summary = mesh_summary(mesh)

    parts = list(mesh.split(only_watertight=False))
    part_info = []
    kept_parts = []
    removed_parts = []
    for idx, part in enumerate(parts):
        info = {
            "index": idx,
            "vertices": int(len(part.vertices)),
            "faces": int(len(part.faces)),
            "watertight": bool(part.is_watertight),
            "bounds_min": [float(x) for x in part.bounds[0]],
            "bounds_max": [float(x) for x in part.bounds[1]],
        }
        part_info.append(info)
        if len(part.faces) >= min_component_faces:
            kept_parts.append(part)
        else:
            removed_parts.append(info)

    if not kept_parts:
        raise RuntimeError("No components survived filtering")

    merged = trimesh.util.concatenate(kept_parts)
    merged.remove_unreferenced_vertices()
    merged_summary = mesh_summary(merged)

    vox = merged.voxelized(pitch=pitch).fill()
    labels, nlabels = ndi.label(vox.matrix)
    if nlabels < 1:
        raise RuntimeError("Voxelization produced empty occupancy")

    repaired = vox.marching_cubes
    repaired.apply_transform(vox.transform)
    sub = repaired.split(only_watertight=False)
    if len(sub) > 1:
        repaired = max(sub, key=lambda p: len(p.faces))
    repaired.remove_unreferenced_vertices()
    repaired.process(validate=True)
    repaired.export(output_path)
    repaired_summary = mesh_summary(repaired)

    report = {
        "input_path": os.path.abspath(input_path),
        "output_path": os.path.abspath(output_path),
        "sha256_input": sha256_file(input_path),
        "sha256_output": sha256_file(output_path),
        "parameters": {"pitch": pitch, "min_component_faces": min_component_faces},
        "original": asdict(original_summary),
        "components_detected": part_info,
        "removed_small_components": removed_parts,
        "merged_input_after_component_filter": asdict(merged_summary),
        "voxel": {
            "shape": [int(x) for x in vox.shape],
            "filled_voxel_count": int(vox.filled_count),
            "connected_components": int(nlabels),
        },
        "repaired": asdict(repaired_summary),
    }
    if summary_path:
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    return report

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_path")
    ap.add_argument("output_path")
    ap.add_argument("--summary", dest="summary_path")
    ap.add_argument("--pitch", type=float, default=0.25)
    ap.add_argument("--min-component-faces", type=int, default=100)
    args = ap.parse_args()
    repair_mesh(args.input_path, args.output_path, args.summary_path, args.pitch, args.min_component_faces)

if __name__ == "__main__":
    main()
