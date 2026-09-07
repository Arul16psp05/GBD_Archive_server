# GBD_Archive_server
 A server to host and distribute the GBD-DART pulsar data.

## Overview
This repository hosts the interactive, astrophysics-themed web archive for the Gauribidanur Diamond Array Radio Telescope (GBD-DART) pulsar project. It operates as a local access node for high-speed data retrieval, displaying observation data, metadata, and long-term trends. 

## Key Features
* **Calendar Browser**: An interactive, calendar-based file browser to navigate daily observations.
* **Stokes Polarization Plots**: Automatically parses metadata arrays to plot 1D Stokes profiles (I, Q, U, V) using a responsive "line and dot" Plotly.js style.
* **All-Time Trends**: A built-in crawler aggregates daily JSON metadata across the archive to plot variables like Dispersion Measure and Folding Period over time.
* **Advanced Filtering**: Features real-time, dual-slider controls (Min SNR and Max Error) to filter trend data based on signal quality and measurement uncertainty.

## Directory & Data Structure
Because this archive relies on a database-free architecture powered by Python's `http.server`, it uses JavaScript to dynamically crawl directories. Data must be mounted in the predefined `PARENT_DIR` following this format: `[PARENT_DIR]/[PULSAR_NAME]/YYYY/MM/DD/`.
[Directory Structure](doc/directory_structure.txt)

Each daily folder must include a `metadata.json` file containing:
* Base scalar values like `Integration_Time_sec` and `SNR`.
* Associated uncertainty values designated by an `_err` suffix (e.g., `Dispersion_Measure_err`).
* Array data for `Profile_bins`, `I`, `Q`, `U`, and `V`.

[![Preview](docs/GBD-DART_Intranet_Archive.png)](docs/GBD-DART_Intranet_Archive.pdf)

## Setup Instructions
1. Clone this repository to your local observatory node.
2. Organize your uncalibrated baseband files, dynamic spectra, and `metadata.json` files into the required date-based directory structure.
3. Start a local server in the project root by running: `python3 -m http.server 8000`.
4. Navigate your browser to `http://localhost:8000` to access the dark-themed UI.

**Data Citation:**
If you use data or code from this archive, we request that you cite the foundational commissioning paper:

*GBD-DART-I: Pulsars and transient source observation between 130 and 350 MHz at Gauribidanur*
A. Pandian B., J. Bagchi, P. Thiagaraj, et al. (2026).
Publications of the Astronomical Society of Australia (PASA).
DOI: [10.1017/pasa.2026.10231](https://doi.org/10.1017/pasa.2026.10231)
