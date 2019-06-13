# On-the-fly machine learning for improving image resolution in tomography

This package contains code accompanying the manuscript of "On-the-fly
machine learning for improving image resolution in tomography".


* Free software: GNU General Public License v3
* Documentation: [https://ahendriksen.github.io/on_the_fly]


## Getting Started

It takes a few steps to setup On the fly machine learning for improving image resolution in tomography on your
machine. We recommend installing
[Anaconda package manager](https://www.anaconda.com/download/) for
Python 3.

### Requirements

To install and execute the code in this package, conda on 64-bit Linux
is required. Moreover, a CUDA 9.0-compatible graphics card and runtime
is required.

### Installing

To install this package, use conda and clone this GitHub project.
To install the package into a new conda environment named `otf`, execute the following in the terminal:
```
conda create -n otf python=3.6
source activate otf
conda install -c astra-toolbox/label/dev  -c aahendriksen -c pytorch -c conda-forge -c owlas \
        msd_pytorch=0.5.1 \
        cudatoolkit=9.0 \
        flexdata \
        tomopy \
        dxchange \
        astra-toolbox=1.9.0.dev10 \
        cone_balls=0.2.2
conda install h5py ipython matplotlib numexpr pyopengl pyqtgraph scikit-image tqdm

# Now install the package using pip
git clone https://github.com/ahendriksen/on_the_fly.git
cd on_the_fly
pip install .
```

### Running the examples

To learn more about the functionality of the package check out our
examples folder.

The examples folder has the following hierarchy:
```
examples
├── cone_foam_fast
│   ├── cone_balls_spec.txt
│   ├── geometries
│   └── Makefile
├── cone_foam_full
│   ├── cone_balls_spec.txt
│   ├── geometries
│   └── Makefile
└── cone_foam_just_roi
    ├── cone_balls_spec.txt
    ├── geometries
    └── Makefile
```

The examples directory contains three directories with a Makefile. The
`cone_foam_full` directory contains the specification of the data as
it is used in the paper. Because generating each projection dataset
can take 2 hours with a recent GPU, I have created
`cone_foam_just_roi` where all voids have been removed that do not
intersect the upper or central region of interest, and
`cone_foam_fast` in which 90% of the voids have been
removed. Generating the projections of `cone_foam_fast` should take
roughly 10 minutes per projection dataset on a modern GPU.

Each directory contains a Makefile that can be used to generate

  * Projection data
  * Reconstructions
  * Training and test sets

Moreover, the makefile contains instructions to train the networks and
to process the input of the test set with the trained neural networks.

#### Generating projections

To generate projection data of the entire foam ball, a zoomed-in
central region of interest, and a zoomed-in upper region of interest,
run:

``` shell
make data/zoom1/.dirstamp
make data/zoom4_centre/.dirstamp
make data/zoom4_top/.dirstamp
```

#### Reconstructing

To reconstruct the entire volume and the regions of interest, run the
following. All intermediate projection data will be saved in the
`processing` directory.

``` shell
make reconstruction/zoom/.dirstamp
make reconstruction/zoom4_centre/.dirstamp
make reconstruction/zoom4_top/.dirstamp

```

#### Generating training and testing datasets

The following commands will generate the training and test set.

``` shell
make training_set
make test_set
```

#### Training

To train a neural network, execute either one of

``` shell
make weights/unet-B1.torch
make weights/unet-A1.torch
make weights/unet-A9.torch
make weights/msd-B1.torch
make weights/msd-A1.torch
make weights/msd-A9.torch
```

To train for more than one epoch, make sure to edit the variable named
`EPOCH` at the top of the `Makefile`.

### Testing

To see how a neural network performs on the test set, execute either one of

``` shell
make test/output-unet-B/.dirstamp
make test/output-unet-A1/.dirstamp
make test/output-unet-A9/.dirstamp
make test/output-msd-B/.dirstamp
make test/output-msd-A1/.dirstamp
make test/output-msd-A9/.dirstamp
make test/output-bicubic/.dirstamp
```

Another option is to bicubically upsample the whole volume. This is
performed on the last line.

## Authors and contributors

* **Allard Hendriksen** - *Initial work*

See also the list of [contributors](https://github.com/ahendriksen/on_the_fly/contributors) who participated in this project.

## Acknowledgements

* We thank [milesial](https://github.com/milesial) for making
  [available](https://github.com/milesial/Pytorch-UNet) a high-quality
  pytorch version of the U-net network architecture.

## How to contribute

If you have any issues, questions, or remarks, then please open an issue on GitHub.

## License

This project is licensed under the GNU General Public License v3 - see the [LICENSE.md](LICENSE.md) file for details.
