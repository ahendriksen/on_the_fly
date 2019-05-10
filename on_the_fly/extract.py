from pathlib import Path
from sacred.observers import MongoObserver
from sacred import Experiment
from os import environ
import on_the_fly.utils as utils
import on_the_fly.tomo as tomo
import on_the_fly.geometry as geom
import numpy as np


ex = Experiment('Extract subvolume from volume data', ingredients=[])

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
    mask_volume_geometry = None   # noqa: Path to volume geometry that describes the data that is extracted


@ex.automain
def main(input_dir, output_dir, volume_geometry, mask_volume_geometry):
    vol_data = tomo.load_stack(input_dir)
    print("Input data shape: ", vol_data.shape)

    vg = tomo.load_geometry(volume_geometry)
    mask_vg = tomo.load_geometry(mask_volume_geometry)
    mask_idx = geom.calculate_mask_index(vg, mask_vg)

    output = vol_data[mask_idx]
    print("Output data shape: ", output.shape)
    tomo.save_stack(output_dir, output)
    utils.print_run(ex, output_dir)


def entry_main():
    ex.run_commandline()
