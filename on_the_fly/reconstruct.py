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

ex = Experiment('Reconstruct', ingredients=[])

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
    input_path = 'normalized_projections' # noqa: Input dir (contains reconstruction / volume data)
    scan_type = 'tomcat'                  # noqa: tomcat, flexray, or simulation
    output_dir = 'reconstruction'         # noqa: Output dir
    volume_geometry = None                # noqa: The path to a pickled astra volume geometry
    projection_geometry = None            # noqa: The path to a pickled astra projection geometry
    rot_center = 882.11                   # noqa: The rotation center
    angle_offset = 0.0                    # noqa: What to add to all angles
    mask_ratio = 0.9                      # noqa: The ratio to (not) mask in circular mask


def reconstruct_tomcat(proj, angle_offset, rot_center):
    theta = tomopy.angles(proj.shape[0]) + angle_offset
    recon = tomopy.recon(proj, theta, center=rot_center, algorithm='gridrec')
    # rot_center = tomopy.find_center(proj, theta, init=882, ind=0, tol=0.5)
    print(f"Reconstruction shape: {recon.shape}")

    recon = tomopy.circ_mask(recon, axis=0, ratio=0.90)
    return recon


def reconstruct_flexray(proj, volume_geometry, projection_geometry):
    proj = tomo.flex2astra(proj)
    recon_id, recon = tomo.fdk(proj, volume_geometry, projection_geometry)
    return recon


def reconstruct_simulation(proj, volume_geometry, projection_geometry):
    proj = tomo.proj2sino(proj)
    recon_id, recon = tomo.fdk(proj, volume_geometry, projection_geometry)
    return recon


@ex.automain
def main(input_path, scan_type, output_dir, volume_geometry,
         projection_geometry, rot_center, angle_offset, mask_ratio):
    if volume_geometry is not None:
        volume_geometry = tomo.load_geometry(volume_geometry)
    if projection_geometry is not None:
        projection_geometry = tomo.load_geometry(projection_geometry)

    input_path = Path(input_path).expanduser().resolve()
    print(f"Reading from {input_path}")
    proj = tomo.load_stack(input_path)
    print(f"Projection shape: {proj.shape}")

    if scan_type == "tomcat":
        recon = reconstruct_tomcat(proj, angle_offset, rot_center)
    if scan_type == "flexray":
        recon = reconstruct_flexray(proj, volume_geometry, projection_geometry)
    if scan_type == "simulation":
        recon = reconstruct_simulation(proj, volume_geometry, projection_geometry)

    output_dir = Path(output_dir).expanduser().resolve()
    print(f"Saving to {output_dir}")
    tomo.save_stack(output_dir, recon)
    utils.print_run(ex, output_dir)


def entry_main():
    ex.run_commandline()
