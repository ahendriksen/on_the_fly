import tifffile
from tqdm import tqdm
from pathlib import Path
from sacred.observers import MongoObserver
from sacred import Experiment
from os import environ
import on_the_fly.utils as utils
import torch
from msd_pytorch.msd_reg_model import MSDRegressionModel
from on_the_fly.unet import UNetRegressionModel
from on_the_fly.dataset import (ImageDataset, BatchSliceDataset)
from torch.utils.data import DataLoader

ex = Experiment('Process volume with neural network', ingredients=[])

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
    weights_file = None    # noqa: Which network weights to use
    network = 'msd'        # noqa: unet or msd
    slab_size = 1          # noqa:


@ex.automain
def main(input_dir, output_dir, weights_file, network, slab_size):
    # Make network
    model = None
    net_opts = dict(depth=100, width=1, loss_function='L2',
                    dilation='MSD', reflect=True, conv3d=False)

    if network == 'msd':
        model = MSDRegressionModel(
            c_in=slab_size,
            c_out=1,
            **net_opts,
        )
    if network == 'unet':
        model = UNetRegressionModel(
            c_in=slab_size,
            c_out=1,
            **net_opts,
        )

    if model is None:
        print("Make sure you have specified the right model")
        return 1

    # Load network
    if weights_file is None:
        print("weights_file parameter is required")
        return
    weights_file = Path(weights_file).expanduser().resolve()
    model.load_network(save_file=weights_file)

    # Load input data
    input_dir = Path(input_dir).expanduser().resolve()
    input_spec = input_dir / '*.tif'
    ds = ImageDataset(input_spec, input_spec)
    ds = BatchSliceDataset(ds, slab_size // 2, slab_size // 2, reflect=True)
    dl = DataLoader(ds, batch_size=1, shuffle=False, num_workers=2)

    # Prepare output directory
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(exist_ok=True)

    # Put network in evaluation mode: this is useful for batchnorm.
    model.net.eval()
    with torch.no_grad():
        for (i, (inp, _)) in tqdm(enumerate(dl), mininterval=5.0):
            model.set_input(inp)
            output = model.net(model.input)
            output = output.detach().cpu().squeeze().numpy()
            output_path = str(output_dir / f"processed_{i:05d}.tif")
            tifffile.imsave(output_path, output)

    utils.print_run(ex, output_dir)


def entry_main():
    ex.run_commandline()
