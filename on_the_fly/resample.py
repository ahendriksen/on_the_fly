import tifffile
from tqdm import tqdm
import skimage.transform as skt
from pathlib import Path
from sacred.observers import MongoObserver
from sacred import Experiment
from os import environ
import on_the_fly.utils as utils
import on_the_fly.tomo as tomo
import on_the_fly.geometry as geom
import numpy as np


ex = Experiment('Up- or down-sample data', ingredients=[])

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
    input_dir = 'input'    # noqa: Input dir (contains reconstruction / volume data)
    output_dir = 'output'  # noqa: Output dir
    factor = 4             # noqa: By how much to resample
    direction = 'up'       # noqa: up=Upsample or down=Downsample
    method = 'bicubic'     # noqa: bicubic or nn=nearest neighbour


def bicubic(input_vol, output_dir, factor, up=True):
    output_dir = Path(output_dir).expanduser().resolve()

    if up:
        output_shape = tuple(factor * s for s in input_vol.shape)
    else:
        output_shape = tuple(s // factor for s in input_vol.shape)

    slab_size = 6 * factor
    j = 0
    print(f"From {input_vol.shape} -> {output_shape} in steps of {slab_size}")
    print(f"Saving in {output_dir}")

    for k in range(0, len(input_vol), slab_size):
        pad = 2 * factor
        a = max(0, k - pad)
        b = min(k + slab_size + pad, len(input_vol))

        slab_input = input_vol[a:b]
        if up:
            slab_output_shape = tuple(s * factor for s in slab_input.shape)
        else:
            slab_output_shape = tuple(s // factor for s in slab_input.shape)

        output = skt.resize(
            slab_input,
            slab_output_shape,
            order=3,
            mode="reflect",
            clip=True,
            preserve_range=True,
        ).astype(np.float32)

        a_pad = k - a
        if up:
            output = output[factor * a_pad: factor * (a_pad + slab_size)]
        else:
            output = output[a_pad // factor: (a_pad + slab_size) // factor]

        for o in tqdm(output):
            tifffile.imsave(str(output_dir / f"output_{j:05}.tif"), o)
            j += 1


@ex.automain
def main(input_dir, output_dir, factor, direction, method):
    vol_data = tomo.load_stack(input_dir)
    print("Input data shape: ", vol_data.shape)

    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(exist_ok=True)

    if direction == 'up' and method == 'bicubic':
        print("upsampling with bicubic")
        bicubic(vol_data, output_dir, factor, up=True)
    if direction == 'up' and method == 'nn':
        print("upsampling with nearest neighbour")
        output = vol_data.repeat(factor, 0).repeat(factor, 1).repeat(factor, 2)
        tomo.save_stack(output_dir, output)
    if direction == 'down' and method == 'nn':
        print("downsampling with nearest neighbour")
        output = vol_data[::factor, ::factor, ::factor]
        tomo.save_stack(output_dir, output)
        pass
    if direction == 'down' and method == 'bicubic':
        print("downsampling with bicubic")
        bicubic(vol_data, output_dir, factor, up=False)
        pass

    utils.print_run(ex, output_dir)


def entry_main():
    ex.run_commandline()
