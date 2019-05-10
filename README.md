# On-the-fly machine learning for improving image resolution in tomography

This package contains code for the manuscript of "On-the-fly machine
learning for improving image resolution in tomography".



* Free software: GNU General Public License v3
* Documentation: [https://ahendriksen.github.io/on_the_fly]


## Readiness

The author of this package is in the process of setting up this
package for optimal usability. The following has already been completed:

- [ ] Documentation
    - A package description has been written in the README
    - Documentation has been generated using `make docs`, committed,
        and pushed to GitHub.
	- GitHub pages have been setup in the project settings
	  with the "source" set to "master branch /docs folder".
- [ ] An initial release
	- In `CHANGELOG.md`, a release date has been added to v0.1.0 (change the YYYY-MM-DD).
	- The release has been marked a release on GitHub.
	- For more info, see the [Software Release Guide](https://cicwi.github.io/software-guides/software-release-guide).
- [ ] A conda package
    - Required packages have been added to `setup.py`, for instance,
      ```
      requirements = [
          # Add your project's requirements here, e.g.,
          # 'astra-toolbox',
          # 'sacred>=0.7.2',
          # 'tables==3.4.4',
      ]
      ```
      has been replaced by
      ```
      requirements = [
          'astra-toolbox',
          'sacred>=0.7.2',
          'tables==3.4.4',
      ]
      ```
    - All "conda channels" that are required for building and
      installing the package have been added to the
      `Makefile`. Specifically, replace
      ```
      conda_package:
        conda install conda-build -y
        conda build conda/
      ```
      by
      ```
      conda_package:
        conda install conda-build -y
        conda build conda/ -c some-channel -c some-other-channel
      ```
    - Conda packages have been built successfully with `make conda_package`.
    - These conda packages have been uploaded to
      [Anaconda](https://anaconda.org). [This](http://docs.anaconda.com/anaconda-cloud/user-guide/getting-started/#cloud-getting-started-build-upload)
      is a good getting started guide.
    - The installation instructions (below) have been updated. Do not
      forget to add the required channels, e.g., `-c some-channel -c
      some-other-channel`, and your own channel, e.g., `-c ahendriksen`.


## Getting Started

It takes a few steps to setup On the fly machine learning for improving image resolution in tomography on your
machine. We recommend installing
[Anaconda package manager](https://www.anaconda.com/download/) for
Python 3.

### Installing

To install this package, use conda and clone this GitHub project.
The installation instructions are as follows:
```
conda create -y -n otf python=3.6
source activate otf
conda install -c astra-toolbox/label/dev  -c aahendriksen -c pytorch -c conda-forge -c owlas \
		msd_pytorch \
		cudatoolkit=9.0 \
		flexdata \
		tomopy \
		dxchange \
		astra-toolbox \
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

examples
├── check_recon_astra.py
├── check_recon_astra.py~
├── cone_foam_fast
│   ├── cone_balls_spec.txt
│   ├── geometries
│   ├── Makefile
├── cone_foam_full
│   ├── cone_balls_spec.txt
│   └── geometries
├── cone_foam_just_roi
│   ├── cone_balls_spec.txt
│   └── geometries





## Authors and contributors

* **Allard Hendriksen** - *Initial work*

See also the list of [contributors](https://github.com/ahendriksen/on_the_fly/contributors) who participated in this project.

## How to contribute

Contributions are always welcome. Please submit pull requests against the `master` branch.

If you have any issues, questions, or remarks, then please open an issue on GitHub.

## License

This project is licensed under the GNU General Public License v3 - see the [LICENSE.md](LICENSE.md) file for details.
