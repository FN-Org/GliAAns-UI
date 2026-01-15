# Code Organization

The project is structured into well-defined modules that separate the graphical interface, pipeline logic, deep learning components, utilities, and resources. Below is an overview of the main directories and their roles.

---

## **Top-Level Files**

* **main.py** – Entry point of the application. Initializes the GUI and the controller.
* **controller.py** – Handles page transitions, workflow state, and coordination of all steps in the multi-page interface.
* **page.py** – Base class for all wizard-style interface pages.
* **logger.py** – Centralized logging utilities.
* **utils.py** – General helper functions used across modules.
* **requirements.txt** – Project-wide dependencies.

---

## **components/**

Contains reusable PyQt6 custom widgets used throughout the GUI, such as:

* File and folder selection components
* Collapsible information frames
* NIfTI selection dialogs
* Custom progress bars
* Graphic views

These components ensure modularity and cleaner UI pages.

---

## **ui/**

Includes all GUI pages and views that define the multi-step workflow of the application:

* Patient selection pages
* Import and NIfTI viewer pages
* Skull stripping, mask selection, and pipeline review pages
* Deep Learning configuration and execution pages
* Workspace tree viewer
* Main window definitions

Each file implements a step or visual tool used in the wizard interface.

---

## **threads/**

Contains threaded workers that execute heavy tasks asynchronously, keeping the UI responsive:

* DICOM/NIfTI import threads
* Skull stripping and preprocessing threads
* Deep Learning worker
* Utility threads for image operations

---

## **deep_learning/**

Implements the Deep Learning module:

* Preprocessing and postprocessing routines
* Coregistration utilities
* nnUNet-based segmentation model
* DALI and PyTorch data loaders
* Checkpoints, atlas files, and configuration utilities

---

## **pediatric_fdopa_pipeline/**

Includes the official FDOPA processing pipeline integrated into the GUI:

* Analysis utilities
* ROI selection
* Pipeline runner
* Quality control routines
* Standard atlas files

The GUI orchestrates and visualizes the output of this module.

---

## **resources/**

Icons, logos, and graphical assets used throughout the interface.

---

## **translations/**

Contains translation files (`it.ts`, `it.qm`) enabling multilingual support.

---

## About **tests**

The project includes a dedicated test suite located in: [/src/tests](./../tests/).

Tests can be inspected and evaluated using the [coverage report](./../tests/htmlcov/index.html), which provides a detailed view of tested modules and execution coverage.


