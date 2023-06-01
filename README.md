# TaxoPhase

Reconstruct haplotypes and produce genealogy graphs from population data.


### Windows and macOS Executables
Download and run the standalone executables without installing Python.</br>
[See the latest release here.](https://github.com/iTaxoTools/TaxoPhase/releases/latest)


### Installing from source
Clone and install the latest version (requires Python 3.10.2 or later):
```
git clone https://github.com/iTaxoTools/TaxoPhase.git
cd TaxoPhase
pip install . -f packages.html
```


## Usage
To launch the GUI, please use:
```
taxophase-gui
```


### Packaging

It is recommended to use PyInstaller from within a virtual environment:
```
pip install ".[dev]" -f packages.html
pyinstaller scripts/taxophase.spec
```
