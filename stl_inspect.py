#!/usr/bin/env python3
import argparse, hashlib, json, os
import numpy as np
import trimesh


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def mesh_stats(path: str) -> dict:
    mesh = trimesh.load_mesh(path, force='mesh')
    inv = mesh.edges_unique_inverse
    counts = np.bincount(inv, minlength=len(mesh.edges_unique))
    return {
        'file': os.path.basename(path),
        'sha256': sha256(path),
        'vertices': int(len(mesh.vertices)),
        'faces': int(len(mesh.faces)),
        'watertight': bool(mesh.is_watertight),
        'components': int(len(mesh.split(only_watertight=False))),
        'boundary_unique_edges': int((counts == 1).sum()),
        'nonmanifold_unique_edges': int((counts > 2).sum()),
        'euler_number': int(mesh.euler_number),
        'bounds_min': mesh.bounds[0].tolist(),
        'bounds_max': mesh.bounds[1].tolist(),
        'extents_xyz': mesh.extents.tolist(),
        'surface_area': float(mesh.area),
        'signed_volume': float(mesh.volume),
        'winding_consistent': bool(mesh.is_winding_consistent),
        'units': 'same units as STL source (typically mm)',
    }


def main():
    parser = argparse.ArgumentParser(description='Inspect one or more STL files with trimesh.')
    parser.add_argument('paths', nargs='+')
    args = parser.parse_args()
    results = [mesh_stats(p) for p in args.paths]
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
