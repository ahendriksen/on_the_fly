from pathlib import Path
from sacred.observers import MongoObserver
from sacred import Experiment
from os import environ
import on_the_fly.utils as utils
import on_the_fly.tomo as tomo
import numpy as np
import numexpr as ne


ex = Experiment('Subtract tiffstacks: calculate a - b', ingredients=[])

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
    a = None                    # noqa: tiff stack a
    b = None                    # noqa: tiff stack b
    output_dir = 'output'       # noqa: output directory


@ex.automain
def main(a, b, output_dir):
    a = tomo.load_stack(a)
    b = tomo.load_stack(b)

    print("a shape: ", a.shape)
    print("b shape: ", b.shape)

    output = np.empty(a.shape, a.dtype)
    ne.evaluate('a-b', out=output)

    tomo.save_stack(output_dir, output)
    utils.print_run(ex, output_dir)


def entry_main():
    ex.run_commandline()
