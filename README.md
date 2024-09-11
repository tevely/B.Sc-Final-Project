# BGU-Raicol

## Installation steps

### 1. Install python engine
Install conda python package manager to manage python environments.
I recommend [miniconda](https://docs.anaconda.com/free/miniconda/miniconda-install/) distribution on x86 platforms and [miniforge](https://github.com/conda-forge/miniforge?tab=readme-ov-file#install) on Apple silicon.

Once installed create conda/mamba environment with python 3.11 and [pipenv](https://pipenv.pypa.io/en/latest/) installed
```
conda create -n py311 python=3.11 pipenv
```

**Note** environment name can be arbitrary, **py311** is used here as an example.

### 2. Install MATLAB
Install [MATLAB](https://www.mathworks.com/downloads) **R2023b**.

**Important**: architecture of MATLAB must match architecture of python distribution.
For instance, if you installed Apple Silicon python distribution in the previous step, you need Apple Silicon version of MATLAB as well.

After installation, open MATLAB, go to **Home>Add-Ons>Get Add-Ons**, type **wgmodes** in "Search for add-ons" field "Waveguide Mode Solver" add-on.

After the add-on is installed, you can close MATLAB.

### 3. Install project's python dependencies
**After** installing MATLAB activate the conda environment created in the first step, navigate to the project root directory, and install the packages using pipenv.
```
conda activate py311
cd <path_to_project>/BGU-Raicol
pipenv install --dev
```
The packages are specified specified in `Pipfile` and `Pipfile.lock` 

## Usage

Before running the simulation scripts it is convenient to activate pipenv shell and navigate to `scripts` directory
```
pipenv shell
cd scripts
```

- `python doubletrack.py` - Calculate modes of a doubletrack waveguide
- `python optimize.py` - Run optimization of waveguide parameters. Needs `hp_space.json` configuration file to be present in `scripts`.
- `python analyze_data.py` - Visualize optimization results.

