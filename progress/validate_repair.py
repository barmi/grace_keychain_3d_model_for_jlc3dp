
#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from repair_stl import repair_mesh

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def sample_bidirectional_distance(mesh_a: trimesh.Trimesh, mesh_b: trimesh.Trimesh, samples: int = 5000) -> dict:
    a_pts, _ = trimesh.sample.sample_surface(mesh_a, samples, seed=1234)
    b_pts, _ = trimesh.sample.sample_surface(mesh_b, samples, seed=1234)
    tree_a = cKDTree(a_pts)
    tree_b = cKDTree(b_pts)
    dist_a_to_b, _ = tree_b.query(a_pts, k=1)
    dist_b_to_a, _ = tree_a.query(b_pts, k=1)
    return {
        "samples_per_mesh": samples,
        "a_to_b_mean": float(np.mean(dist_a_to_b)),
        "a_to_b_max": float(np.max(dist_a_to_b)),
        "b_to_a_mean": float(np.mean(dist_b_to_a)),
        "b_to_a_max": float(np.max(dist_b_to_a)),
    }

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("original_stl")
    p.add_argument("reference_repaired_stl")
    p.add_argument("generated_stl")
    p.add_argument("--json", required=True, dest="json_path")
    p.add_argument("--previous-repaired", default=None)
    args = p.parse_args()

    tmp_summary = args.json_path + ".regen_summary.json"
    regen = repair_mesh(args.original_stl, args.generated_stl, summary_path=tmp_summary)

    reference_hash = sha256_file(args.reference_repaired_stl)
    generated_hash = sha256_file(args.generated_stl)

    ref_mesh = trimesh.load_mesh(args.reference_repaired_stl, force="mesh")
    gen_mesh = trimesh.load_mesh(args.generated_stl, force="mesh")
    result = {
        "reference_repaired_stl": os.path.abspath(args.reference_repaired_stl),
        "generated_stl": os.path.abspath(args.generated_stl),
        "reference_sha256": reference_hash,
        "generated_sha256": generated_hash,
        "exact_hash_match": reference_hash == generated_hash,
        "reference_vs_generated": sample_bidirectional_distance(ref_mesh, gen_mesh),
        "regeneration_summary": regen,
    }
    if args.previous_repaired and os.path.exists(args.previous_repaired):
        prev_mesh = trimesh.load_mesh(args.previous_repaired, force="mesh")
        result["previous_repaired_stl"] = os.path.abspath(args.previous_repaired)
        result["previous_repaired_sha256"] = sha256_file(args.previous_repaired)
        result["previous_vs_generated"] = sample_bidirectional_distance(prev_mesh, gen_mesh)

    with open(args.json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
