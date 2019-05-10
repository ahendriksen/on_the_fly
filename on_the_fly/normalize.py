from os import environ
from pathlib import Path
from sacred import Experiment
from sacred.observers import MongoObserver
import dxchange
import numexpr as ne
import numpy as np
import on_the_fly.tomo as tomo
import on_the_fly.utils as utils
import pyqtgraph as pq
import tifffile
import tomopy
from tqdm import tqdm
from scipy import ndimage

ex = Experiment('Normalize projection data', ingredients=[])

mongo_enabled = environ.get('MONGO_SACRED_ENABLED')
mongo_user = environ.get('MONGO_SACRED_USER')
mongo_pass = environ.get('MONGO_SACRED_PASS')
mongo_host = environ.get('MONGO_SACRED_HOST')

if mongo_enabled == 'true':
    assert mongo_user, 'Setting $MONGO_USER is required'
    assert mongo_pass, 'Setting $MONGO_PASS is required'
    assert mongo_host, 'Setting $MONGO_HOST is required'

    mongo_url = 'mongodb://{0}:{1}@{2}:27017/sacred?authMechanism=SCRAM-SHA-1'.format(
        mongo_user, mongo_pass, mongo_host)

    ex.observers.append(MongoObserver.create(url=mongo_url, db_name='sacred'))


@ex.config
def cfg():
    input_path = 'input'  # noqa: Input dir (contains reconstruction / volume data)
    scan_type = 'tomcat'   # noqa:
    output_dir = 'normalized_projections'    # noqa: Output dir
    rotation_angle = 0.0                     # noqa: rotate projection images


def process_tomcat(input_path):
    input_path = Path(input_path).expanduser().resolve()
    print(f"Reading from {input_path}")
    proj, flat, dark = dxchange.read_sls_tomcat(str(input_path))

    print(f"Projection shape: {proj.shape}")
    print(f"Flats shape:      {flat.shape}")
    print(f"Darks shape:      {dark.shape}")

    proj = tomopy.normalize(proj, flat, dark)
    proj = tomopy.minus_log(proj)
    return proj


def process_flexray(input_path):
    input_path = Path(input_path).expanduser().resolve()
    print(f"Reading from {input_path}")
    opts = dict(dtype=np.float32)
    proj = tomo.load_tiffs(sorted(input_path.glob("scan_*.tif")), **opts)
    flat = tomo.load_tiffs(sorted(input_path.glob("io*.tif")), **opts)
    dark = tomo.load_tiffs(sorted(input_path.glob("di*.tif")), **opts)

    print(f"Projection shape: {proj.shape}")
    print(f"Flats shape:      {flat.shape}")
    print(f"Darks shape:      {dark.shape}")

    flat_mean = flat.mean(0)    # noqa:F841 (is used in ne.evaluate)
    ne.evaluate('-log((proj - dark) / ((flat_mean - dark)))', out=proj)

    return proj


@ex.automain
def main(input_path, scan_type, rotation_angle, output_dir):
    if scan_type == 'tomcat':
        proj = process_tomcat(input_path)
    if scan_type == 'flexray':
        proj = process_flexray(input_path)

    if abs(rotation_angle) > 0.0:
        print("Rotating projections")
        for i, p in tqdm(enumerate(proj)):
            proj[i] = ndimage.rotate(p, rotation_angle, reshape=False)

    output_dir = Path(output_dir).expanduser().resolve()
    print(f"Saving to {output_dir}")
    tomo.save_stack(output_dir, proj)
    utils.print_run(ex, output_dir)


def entry_main():
    ex.run_commandline()
