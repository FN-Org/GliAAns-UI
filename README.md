

# GliAAns – Gliomas Automatic AnalysiS
### University of Genoa - DIBRIS

GliAAns is a cross-platform desktop application designed to provide clinicians with an intuitive graphical interface for executing the Pediatric FDOPA Pipeline, a neuroimaging workflow for extracting static and dynamic parameters from 18F-DOPA PET/CT and MRI data in pediatric gliomas (as described in the original methodology [paper](https://www.mdpi.com/2077-0383/13/20/6252#)).

The application simplifies the entire analysis process by guiding the user through data import, preprocessing, VOI selection (manual or automatic), pipeline execution, and results visualization. 

Built with Python and PyQt6, it integrates state-of-the-art imaging libraries and an optional Deep Learning–based segmentation model (CUDA-enabled Linux systems).
GliAAns is developed to run entirely offline, ensuring patient data privacy and compatibility with hospital workstations on Linux, Windows, and macOS.

---

## Key Features
- Wizard-based workflow for clinical usability
- Support for DICOM, NIfTI, and BIDS datasets
- Optional DICOM to NIfTI conversion
- Manual or automatic VOI delineation
- Real-time processing feedback and structured logging
- Export of results in different formats
- Local execution only — no network dependency

## Get Started
To get started, you can find installation and usage instructions in the [manuals](./docs/manuals/) directory:

- [install.md](./docs/manuals/install.md)
- [compile.md](./docs/manuals/compile.md)
- [run.md](./docs/manuals/run.md)
