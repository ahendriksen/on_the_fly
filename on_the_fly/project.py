from pathlib import Path
from sacred.observers import MongoObserver
from sacred import Experiment
from os import environ
import on_the_fly.utils as utils
import on_the_fly.tomo as tomo
import on_the_fly.geometry as geom
import numpy as np


ex = Experiment('Project volume data onto detector geometry', ingredients=[])

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
    input_dir = 'input'           # noqa: Input dir (contains reconstruction / volume data)
    output_dir = 'output'         # noqa: Output dir
    volume_geometry = None        # noqa: Path to volume geometry to use
    mask_volume_geometry = None   # noqa: Path to volume geometry to use as mask
    projection_geometry = None    # noqa: Path to projection geomety to use
    scan_type = 'flexray'         # noqa: tomcat, flexray, or simulation

@ex.automain
def main(input_dir, output_dir, volume_geometry, mask_volume_geometry,
         projection_geometry, scan_type):
    vol_data = tomo.load_stack(input_dir)
    print("Volume data shape: ", vol_data.shape)
    vg = tomo.load_geometry(volume_geometry)
    pg = tomo.load_geometry(projection_geometry)

    # If necessary, mask some of the volume data
    if mask_volume_geometry is not None:
        mask_vg = tomo.load_geometry(mask_volume_geometry)
        mask_idx = geom.calculate_mask_index(vg, mask_vg)
        vol_data[mask_idx] = 0.0

    proj_id, proj_data = tomo.project(vol_data, vg, pg)

    if scan_type == "flexray":
        proj_data = tomo.astra2flex(proj_data)
    if scan_type == "simulation":
        proj_data = tomo.sino2proj(proj_data)

    tomo.save_stack(output_dir, proj_data)
    utils.print_run(ex, output_dir)


def entry_main():
    ex.run_commandline()
