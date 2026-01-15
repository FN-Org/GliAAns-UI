# User Requirements Specification Document (URS)

**DIBRIS – University of Genoa**

**School of Engineering, Software Engineering Course 80154**

**Version**: 1.1

**Authors**: 
<br>Federico Giovanni Garau,
<br>Nicolò Trebino

## Revision History

| Version | Date       | Authors                           | Notes                      |
| ------- | ---------- | --------------------------------- | -------------------------- |
| 1.0     | 2025-05-22 | Federico G. Garau, Nicolò Trebino | Initial release of the URS |
| 1.1     | 2025-06-13 | Federico G. Garau, Nicolò Trebino | Fixing ambiguity and improvements |
| 1.2	  | 2025-10-19 | Federico G. Garau, Nicolò Trebino | Improve clarity |

---

## Table of Contents

1. [Introduction](#1-introduction)
	1. [Scope](#11-scope)
	2. [Definitions and Acronyms](#12-definitions-and-acronyms)
	3. [References](#13-references)
3. [System Overview](#2-system-overview)
   	1. [Context and Motivation](#21-context-and-motivation)
	2. [Project Objectives](#22-project-objectives)
5. [Requirements](#3-requirements)
	1. [Stakeholders](#31-stakeholders)
	2. [Functional Requirements](#32-functional-requirements)
	3. [Non-Functional Requirements](#33-non-functional-requirements)

---

## 1. Introduction

### 1.1 Scope

This document defines the user-level requirements for the development of a local graphical user interface (GUI) for the Pediatric FDOPA Pipeline. This pipeline is a neuroimaging analysis tool designed for the evaluation of pediatric brain tumors using Magnetic Resonance Imaging (MRI) and \[18F]F-DOPA Positron Emission Tomography (PET).

The GUI is intended to simplify data ingestion, automate pipeline execution, and present results in a clinically interpretable format.

### 1.2 Definitions and Acronyms

| Acronym | Definition                                     |
| ------- | ---------------------------------------------- |
| GUI     | Graphical User Interface                       |
| MRI     | Magnetic Resonance Imaging                     |
| PET     | Positron Emission Tomography                   |
| VOI     | Volume of Interest                             |
| PACS    | Picture Archiving and Communication System     |
| NIfTI   | Neuroimaging Informatics Technology Initiative |
| CSV     | Comma-Separated Values                         |
| PDF 	  | Portable Document Format                       |
| BIDS    | Brain Imaging Data Structure                   |
| FDOPA   | Fluorodopa (18F), a PET radiotracer            |
| CUDA	  | Compute Unified Device Architecture			   |
| GPU 	  | Graphics Processing Unit						   |	

### 1.3 References

* [Pediatric FDOPA Pipeline GitHub Repository](https://github.com/MicheleMureddu/Pediatric_fdopa_pipeline)
* [Clinical Paper](https://www.mdpi.com/2077-0383/13/20/6252#)
* [Technical Documentation and Internal Design Discussions](./../ref/)

---

## 2. System Overview

### 2.1 Context and Motivation

The Pediatric FDOPA Pipeline provides a standardized approach for analyzing neuroimaging data in pediatric oncology. Despite its robustness, the current command-line interface limits usability for clinicians without programming expertise.

This project aims to develop a GUI that facilitates local execution of the pipeline, streamlines the analysis process, and supports clinical workflows.

### 2.2 Project Objectives

* Develop a cross-platform GUI as a wizard-based interface guiding the user, clinical personnel, through the pipeline in well-defined steps.
* Support the input of neuroimaging data in DICOM and NIfTI formats.
* Integrate optional DICOM-to-NIfTI conversion.
* Automate the execution of the processing pipeline.
* Display and export the analysis results in both graphical and tabular formats.

---

## 3. Requirements

### Priority Levels

| Symbol | Meaning            |
| ------ | ------------------ |
| M      | Mandatory          |
| D      | Desirable          |
| O      | Optional           |
| E      | Future Enhancement |

---

### 3.1 Stakeholders

| Stakeholder       | Role and Responsibilities                                                               |
| ----------------- | --------------------------------------------------------------------------------------- |
| Medical Personnel | Primary end-users responsible for uploading, processing, and interpreting patient data. |
| Researchers       | Secondary users involved in testing, validation, and further pipeline development.      |

---

### 3.2 Functional Requirements

| ID  | Description                                                                                       | Priority |
| --- | ------------------------------------------------------------------------------------------------- | -------- |
| 1.0   | The system shall allow the user to select multiple patient datasets.                              |         |
| 1.1 | - The system shall guide the user step-by-step to select the correct images for each pipeline step. | M       |
| 1.2 | - The system shall allow batch selection of patient data following the BIDS convention.             | M       |
| 2.0 | The system shall support different input data.   		    				    | 	      |
| 2.1 | - The system shall support input in NifTi (.nii/.nii.gz) format.               			    | M       |
| 2.2 | - The system shall support input in DICOM (.dcm) format.               				    | M       |
| 3.0 | The system shall guide and help the user through each processing step in sequence.     	            | M       |
| 4.0 | The system shall allow the user to choose between manual delineation of the VOI and automatic segmentation using a Deep Learning model. |  |
| 4.1 | - If manual mode is selected, the GUI shall provide tools for assisted "automatic drawing" of the VOI. | M |
| 4.2 | - If automatic mode is selected, the system shall perform segmentation using the integrated Deep Learning model. (Only on linux platform with a CUDA capable GPU) | M |
| 5.0   | The system shall show real-time processing status and notify upon completion or errors.           | M        |
| 6.0   | The system shall organize results per patient in a dedicated output directory.                    | M        |
| 7.0   | The system shall allow exporting results in the following formats:                                |          |
| 7.1 | - CSV                                                                                             | M        |
| 7.2 | - NIfTI                                                                                           | M        |
| 7.3 | - LaTeX                                                                                           | E        |
| 7.4 | - PDF                                                                                             | E        |
| 8.0   | The system shall log all execution steps in human-readable `.json` and `.txt` files.              | M        |
| 9.0   | The system shall present a summary view of results with clickable links for navigation.           | E        |
| 10.0   | The system shall allow saving and resuming incomplete sessions.                                   | E        |
| 11.0  | The system shall allow printing result summaries.                                                 | E        |

---

### 3.3 Non-Functional Requirements

| ID  | Description                                                                                      | Priority |
| --- | ------------------------------------------------------------------------------------------------ | -------- |
| 1   | The system shall function entirely offline, without requiring authentication or internet access. | M        |
| 2   | The system shall be compatible with standard hospital workstations:                              |          |
| 2.1 | - Linux                                                                                          | M        |
| 2.2 | - macOS                                                                                          | M        |
| 2.3 | - Windows                                                                                        | M        |
| 3   | The interface shall be intuitive and require minimal training for clinicians.                    | M        |
| 4   | If non-anonymized data is detected, the GUI shall warn the user via a clear and visible alert.   | E        |
| 5   | The system shall not transmit identifiable information.                                 		 | M        |
| 6   | The system shall ensure logs are available for debugging and traceability.                       | M        |

