from pathlib import Path
from sacred.observers import MongoObserver
from sacred import Experiment
from os import environ
import on_the_fly.utils as utils
import on_the_fly.tomo as tomo
import tifffile
import numpy as np
import numexpr as ne
import pyqtgraph as pq


ex = Experiment('display data', ingredients=[])

@ex.config
def cfg():
    path = "./"
    levels=None
    projections = False
    skip = 1


@ex.automain
def main(path, levels, skip, projections):
    data = tomo.load_stack(path, skip=skip)

    if projections:
        axes = dict(zip("yxt", range(3)))
    else:
        axes = dict(zip("txy", range(3)))

    app = pq.mkQApp()
    pq.image(data, axes=axes, levels=levels)
    pq.ImageView.setImage
    app.exec_()


def entry_main():
    ex.run_commandline()
