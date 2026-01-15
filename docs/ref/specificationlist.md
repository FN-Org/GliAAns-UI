# Specification List

### 1. General Specification

1. The system shall allow the user (a medical doctor) to load one or more patient folders from a local hard drive (desiderable in the future also from the PACS)
2. The system shall allow the user to input patient data in NIFTI or DICOM format.
3. The system shall allow the user to convert DICOM images to NIFTI before processing.
4. The system shall allow the user to run the analysis pipeline on selected patients.
5. The system shall allow the user to save the output of the analysis locally.
6. The system shall allow the user to view the results through an embedded viewer or preview module.
7. The system shall allow the user to export the output in CSV format.
8. The system shall allow the user to open previously processed patient results from the local disk.
9. The system shall allow the user to visualize output NIFTI files using an integrated viewer.
10. The system shall work completely offline and locally, without requiring network access or authentication.

---

### 2. General Information

1. The system shall be intended for use by certified medical personnel and researchers.
2. The system shall process anonymized patient data, ensuring privacy compliance.
3. The system shall operate on local infrastructure (e.g., a workstation in the hospital).

---

### 3. Input/Output Requirements
For more information: [q&a_2](./q&a_2.md)

#### 3.1 Input

1. The system shall accept input in the form of a directory containing:
    * At least one `.nii` or `.nii.gz` PET image (FDOPA).
    * A corresponding `.nii` or `.nii.gz` anatomical MRI (e.g., T1 or FLAIR).
    * A lesion mask (`.nii` or `.nii.gz`), matched by patient ID.
2. The system shall allow the selection of multiple patient folders at once.
3. The system shall automatically validate input folder structure and required files.

#### 3.2 Output

1. The system shall generate, for each processed patient:
    * One CSV file for tumor-to-striatum ratio.
    * One CSV file for dynamic parameters.
    * One CSV file for H_tumor percentage.
    * One folder with processed NIFTI outputs, including spatially normalized volumes and lesion segmentations.

---

### 4. Interface & Usability Requirements

1. The interface shall provide a graphical interface that guides the user through the steps:
    * Load patient data
    * (Optional) Convert DICOM to NIFTI
    * “Automatic drawing” with MRIcroGL
    * Run analysis with python scripts
    * Visualize/export results
2. The interface shall allow users to choose betweeen the normal (manual) steps and the deep learning (automatic) based ones.
3. The interface shall highlight any missing required files before processing begins.
4. The interface shall display error messages if the analysis fails.
5. The interface shall allow the user to preview the following outputs separately:
    * `.nii.gz`
    * `.gif`
    * `.png`
    * (dynamic graphs for future implementation)
6. The interface shall allow exporting logs or reports for debugging or validation purposes.

---

### 5. Pipeline Integration Requirements

1. The system shall integrate the Python pipeline located at [GitHub repository](https://github.com/MicheleMureddu/Pediatric_fdopa_pipeline) also with the new Deep Learning feature.
2. The system shall execute the pipeline using local system resources (CPU/GPU if available).
3. The system shall allow the user to specify optional parameters to the pipeline if needed.
4. The system shall log all analysis steps, inputs, and outputs in a human-readable log file.

---

### 6. Security & Privacy

1. The system shall not store or transmit any identifiable patient information.
2. The system shall ensure that all processed data and intermediate files remain on the local machine.
3. The system shall alert the user if the files used are not anonymous.
