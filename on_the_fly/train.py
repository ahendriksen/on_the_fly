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
from on_the_fly.dataset import (ImageDataset, BatchSliceDataset, CroppingDataset)
from torch.utils.data import DataLoader

ex = Experiment('Train neural network', ingredients=[])

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
    input_dir = 'input'   # noqa: Input dir (contains reconstruction / volume data)
    target_dir = 'target' # noqa: Target dir (contains reconstruction / volume data)
    weights_file = None   # noqa: Where to save network weights
    network = 'msd'       # noqa: unet or msd
    slab_size = 1         # noqa:
    epochs = 1            # noqa: # of epochs to train for


def save_network(model, path):
    path = Path(path).expanduser().resolve()
    # Clear the L and G buffers before saving:
    model.msd.clear_buffers()
    torch.save(model.net.state_dict(), path)


@ex.automain
def main(_run, input_dir, target_dir, weights_file, network,
         slab_size, epochs):
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

    # Load input data
    input_dir = Path(input_dir).expanduser().resolve()
    input_spec = input_dir / '*.tif'
    target_dir = Path(target_dir).expanduser().resolve()
    target_spec = target_dir / '*.tif'

    ds = ImageDataset(input_spec, target_spec)
    ds = CroppingDataset(ds, remove_slices=5, remove_sides=5)
    ds = BatchSliceDataset(ds, slab_size // 2, slab_size // 2, reflect=True)
    dl = DataLoader(ds, batch_size=1, shuffle=False, num_workers=2)

    print("Setting normalization parameters")
    model.set_normalization(dl)

    print("Training...")
    for epoch in tqdm(range(epochs), mininterval=5.0):
        # Train
        training_error = 0.0
        for (input, target) in tqdm(dl, mininterval=5.0):
            model.learn(input, target)
            training_error += model.get_loss()

        training_error = training_error / len(dl)
        _run.log_scalar("Training error", training_error.item())

    # Always save final network parameters
    save_network(model, weights_file)


def entry_main():
    ex.run_commandline()
