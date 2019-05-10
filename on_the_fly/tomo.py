from pathlib import Path
from tqdm import tqdm
import astra
import astra.experimental
import numpy as np
import pickle
import tifffile


def load_geometry(path):
    path = Path(path).expanduser().resolve()
    with open(path, "rb") as f:
        geom = pickle.load(f)
    return geom


def save_geometry(path, geometry):
    path = Path(path).expanduser().resolve()
    with open(path, "wb") as f:
        pickle.dump(geometry, f)


def save_stack(path, data, *, prefix="output", exist_ok=True, parents=False):
    path = Path(path).expanduser().resolve()
    path.mkdir(exist_ok=exist_ok, parents=parents)

    for i, d in tqdm(enumerate(data), mininterval=1.0):
        output_path = path / f"{prefix}_{i:05d}.tif"
        tifffile.imsave(str(output_path), d)


def load_tiffs(paths, squeeze=False, dtype=None):
    img0 = tifffile.imread(str(paths[0]))
    if squeeze:
        img0 = img0.squeeze()
    if dtype is None:
        dtype = img0.dtype

    imgs = np.empty((len(paths), *img0.shape), dtype=dtype)

    for i, p in tqdm(enumerate(paths)):
        img = tifffile.imread(str(p))
        if squeeze:
            img = img.squeeze()
        imgs[i] = img

    return imgs


def load_stack(path, *, skip=1, squeeze=False):
    """Load a stack of tiff files.

    Make sure that the tiff files are sorted *alphabetically*,
    otherwise it is not going to look pretty..

    :param path: path to directory containing tiff files
    :param skip: read every `skip' image
    :param squeeze: whether to remove any empty dimensions from image
    :returns: an np.array containing the values in the tiff files
    :rtype: np.array

    """
    path = Path(path).expanduser().resolve()

    # Only read every `skip' image:
    img_paths = sorted(path.glob("*.tif"))[::skip]

    return load_tiffs(img_paths, squeeze=squeeze)


def project(vol_data, vol_geom, proj_geom):
    vol_id = astra.data3d.create('-vol', vol_geom, vol_data)
    proj_id = astra.data3d.create('-sino', proj_geom)
    projector = astra.create_projector("cuda3d", proj_geom, vol_geom)

    astra.experimental.do_composite_FP(projector, [vol_id], [proj_id])

    return proj_id, astra.data3d.get_shared(proj_id)


def fdk(proj_data, vol_geom, proj_geom):
    vol_id = astra.data3d.create('-vol', vol_geom)
    proj_id = astra.data3d.create('-sino', proj_geom, proj_data)
    projector = astra.create_projector("cuda3d", proj_geom, vol_geom)
    astra.experimental.accumulate_FDK(projector, vol_id, proj_id)

    return vol_id, astra.data3d.get_shared(vol_id)


def flex2astra(proj):
    proj = np.transpose(proj, [1, 0, 2])
    proj = np.flipud(proj)
    return proj


def astra2flex(proj):
    proj = np.flipud(proj)
    proj = np.transpose(proj, [1, 0, 2])
    return proj


def proj2sino(proj):
    proj = np.transpose(proj, [1, 0, 2])
    return proj


def sino2proj(proj):
    proj = np.transpose(proj, [1, 0, 2])
    return proj
