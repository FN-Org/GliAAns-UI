import json
import os
import glob

from PyQt6 import QtGui
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea,
                             QFrame, QGridLayout, QHBoxLayout, QSizePolicy)
from PyQt6.QtCore import Qt, QCoreApplication

from ui.pipeline_review_page import PipelineReviewPage
from utils import resource_path
from page import Page
from logger import get_logger

log = get_logger()


class PipelinePatientSelectionPage(Page):
    """
    This class scans the workspace for patient directories, verifies if the required
    imaging files (FLAIR, skull-stripped, segmentation) are present, and presents
    a visual grid of patient cards. Users can select eligible patients to proceed
    to the pipeline configuration stage.

    Attributes:
        context (dict): The application context containing shared data and state.
        workspace_path (str): The root directory path containing patient data.
        patient_buttons (dict): Maps patient IDs to their selection `QPushButton`.
        selected_patients (set): A set of strings containing IDs of currently selected patients.
        patient_status (dict): Stores eligibility status and missing file details for each patient.
    """

    def __init__(self, context=None, previous_page=None):
        """
        Initializes the PipelinePatientSelectionPage.

        Args:
            context (dict, optional): The shared application context. Defaults to None.
            previous_page (Page, optional): The page instance navigated from. Defaults to None.
        """
        super().__init__()

        self.context = context
        self.previous_page = previous_page
        self.next_page = None

        # Path to the workspace directory containing patient data
        self.workspace_path = context["workspace_path"]

        # Dictionaries to track patient widgets, selected patients, and their processing status
        self.patient_buttons = {}
        self.selected_patients = set()
        self.patient_status = {}  # Stores eligibility and missing data for each patient

        # Initialize the user interface
        self._setup_ui()

        # Set translations (for multilingual UI)
        self._translate_ui()
        if context and "language_changed" in context:
            # Connect language change signal for dynamic translation
            context["language_changed"].connect(self._translate_ui)

    def _setup_ui(self):
        """
        Sets up the main layout and UI components.

        This method initializes the title, the bulk selection control buttons,
        the scrollable area for the patient grid, and the statistical summary widget.
        """
        self.layout = QVBoxLayout(self)

        # --- Title ---
        self.title = QLabel("Select Patients for Pipeline Analysis")
        self.title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(self.title)

        # --- Top buttons (bulk selection controls) ---
        top_buttons_layout = QHBoxLayout()

        self.select_eligible_btn = QPushButton("Select All Eligible")
        self.deselect_all_btn = QPushButton("Deselect All")
        self.refresh_btn = QPushButton("Refresh Status")

        self.buttons = [self.select_eligible_btn, self.deselect_all_btn, self.refresh_btn]

        # Apply a consistent visual style to all buttons
        btn_style = """
            QPushButton {
                background-color: #e0e0e0;
                padding: 10px 20px;
                border-radius: 10px;
                border: 1px solid #bdc3c7;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton:disabled {
                background-color: #f0f0f0;
                color: #888888;
            }
        """
        for btn in self.buttons:
            btn.setStyleSheet(btn_style)

        # Connect buttons to actions
        self.select_eligible_btn.clicked.connect(self._select_all_eligible_patients)
        self.deselect_all_btn.clicked.connect(self._deselect_all_patients)
        self.refresh_btn.clicked.connect(self._refresh_patient_status)

        # Add the buttons to layout with stretch for alignment
        top_buttons_layout.addStretch()
        top_buttons_layout.addWidget(self.select_eligible_btn)
        top_buttons_layout.addWidget(self.deselect_all_btn)
        top_buttons_layout.addWidget(self.refresh_btn)
        self.layout.addLayout(top_buttons_layout)

        # --- Scroll area for displaying patients ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                font-size: 13px;
                border: 1px solid #CCCCCC;
                border-radius: 10px;
                padding: 5px;
            }
        """)

        # Container widget inside scroll area (grid of patient cards)
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

        # --- Summary panel showing total and eligible counts ---
        self.summary_widget = self._create_summary_widget()

        # Add widgets to the main layout
        self.layout.addWidget(self.summary_widget)
        self.layout.addWidget(self.scroll_area)

        # Number of patient columns per row in grid
        self.column_count = 2

        # Load patient data and build UI
        self._load_patients()

    def _create_summary_widget(self):
        """
        Creates a modern-style summary widget for displaying patient statistics.

        Constructs a `QFrame` containing "pill" style cards that display the
        total number of patients, the number of eligible patients, and the
        number of ineligible patients.

        Returns:
            QFrame: The constructed summary widget.
        """
        summary_frame = QFrame()
        summary_frame.setObjectName("summaryCard")
        summary_frame.setStyleSheet("""
            QFrame#summaryCard {
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                background-color: #ffffff;
                padding: 0.1em;
            }
        """)

        main_layout = QVBoxLayout(summary_frame)

        # Section title
        self.title_summary = QLabel(QCoreApplication.translate("PipelinePatientSelectionPage", "Pipeline Requirements Summary"))
        self.title_summary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_summary.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000; margin-bottom: 10px;")
        main_layout.addWidget(self.title_summary)

        # Horizontal layout for summary “pill” cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        # Create pill cards showing totals
        self.total_label = self._create_stat_pill(resource_path("resources/icon_total.png"),
                                                  QCoreApplication.translate("PipelinePatientSelectionPage", "Total Patients"), "0")
        self.eligible_label = self._create_stat_pill(resource_path("resources/icon_check.png"),
                                                     QCoreApplication.translate("PipelinePatientSelectionPage", "Eligible"), "0", color="#27ae60")
        self.not_eligible_label = self._create_stat_pill(resource_path("resources/icon_cross.png"),
                                                         QCoreApplication.translate("PipelinePatientSelectionPage", "Not Eligible"), "0", color="#c0392b")

        # Add pills to layout
        for pill in [self.total_label, self.eligible_label, self.not_eligible_label]:
            pill.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            stats_layout.addWidget(pill)

        main_layout.addLayout(stats_layout)

        return summary_frame

    def _create_stat_pill(self, icon_path, label_text, value_text, color="#000000"):
        """
        Creates a card-like label with an icon, text, and numeric value.

        Args:
            icon_path (str): Path to the icon image (currently unused in the simplified implementation).
            label_text (str): The description label (e.g., "Eligible").
            value_text (str): The numeric value as a string.
            color (str, optional): Hex color code for the numeric value text. Defaults to "#000000".

        Returns:
            QFrame: A frame widget representing the statistic pill.
        """
        pill = QFrame()
        pill.setObjectName("summaryCard")
        pill.setStyleSheet(f"""
            QFrame#summaryCard {{
                border: 1px solid #CCCCCC;
                border-radius: 10px;
                background-color: #f9f9f9;
            }}
        """)

        layout = QVBoxLayout(pill)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Text label (e.g., “Total Patients”)
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 13px; font-weight: bold;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Numeric value (e.g., “5”)
        value = QLabel(value_text)
        value.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")
        value.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)
        layout.addWidget(value)

        # Keep reference to labels for later updates
        pill.label = label
        pill.value_label = value

        pill.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        pill.setMinimumHeight(50)
        pill.setMaximumHeight(120)

        return pill

    def _check_patient_requirements(self, patient_path, patient_id):
        """
        Checks whether a patient meets all necessary pipeline file requirements.

        It looks for the existence of:
        1.  **FLAIR image**: `anat/*_flair.nii[.gz]`
        2.  **Skull-stripped image**: `derivatives/skullstrips/.../anat/*_brain.nii[.gz]`
        3.  **Segmentation/Mask**: `manual_masks` or `deep_learning_seg`

        Args:
            patient_path (str): The absolute path to the patient's folder.
            patient_id (str): The unique identifier of the patient (e.g., 'sub-01').

        Returns:
            dict: A dictionary containing:
                - `eligible` (bool): True if all files are present.
                - `requirements` (dict): Boolean status for each file type ('flair', 'skull_stripping', 'segmentation').
                - `missing_files` (list): List of translated strings describing missing components.
                - `segmentation_type` (str or None): The type of segmentation found ("Manual Mask" or "deep_learning_seg Segmentation").
        """
        # Each key corresponds to a necessary preprocessing step
        requirements = {
            'flair': False,
            'skull_stripping': False,
            'segmentation': False
        }

        missing_files = []  # Collect missing components for display

        # --- 1. Check for FLAIR anatomical image ---
        flair_patterns = [
            os.path.join(patient_path, "anat", "*_flair.nii"),
            os.path.join(patient_path, "anat", "*_flair.nii.gz")
        ]

        flair_found = False
        for pattern in flair_patterns:
            if glob.glob(pattern):  # Search for matching files
                flair_found = True
                break

        requirements['flair'] = flair_found
        if not flair_found:
            missing_files.append(QCoreApplication.translate(
                "PipelinePatientSelectionPage", "FLAIR image (anat/*_flair.nii[.gz])"))

        # --- 2. Check for Skull-Stripped image ---
        skull_strip_patterns = [
            os.path.join(self.workspace_path, "derivatives", "skullstrips", patient_id, "anat", "*_brain.nii"),
            os.path.join(self.workspace_path, "derivatives", "skullstrips", patient_id, "anat", "*_brain.nii.gz")
        ]

        skull_strip_found = False
        for pattern in skull_strip_patterns:
            if glob.glob(pattern):
                skull_strip_found = True
                break

        requirements['skull_stripping'] = skull_strip_found
        if not skull_strip_found:
            missing_files.append(QCoreApplication.translate(
                "PipelinePatientSelectionPage", "Skull stripped image (derivatives/skullstrips/.../anat/*_brain.nii[.gz])"))

        # --- 3. Check for Segmentation or Manual Mask ---
        segmentation_patterns = [
            # Manual masks
            os.path.join(self.workspace_path, "derivatives", "manual_masks", patient_id, "anat", "*_mask.nii"),
            os.path.join(self.workspace_path, "derivatives", "manual_masks", patient_id, "anat", "*_mask.nii.gz"),
            # Deep learning segmentation output
            os.path.join(self.workspace_path, "derivatives", "deep_learning_seg", patient_id, "anat", "*_seg.nii"),
            os.path.join(self.workspace_path, "derivatives", "deep_learning_seg", patient_id, "anat", "*_seg.nii.gz")
        ]

        segmentation_found = False
        segmentation_type = None
        for pattern in segmentation_patterns:
            if glob.glob(pattern):
                segmentation_found = True
                # Identify segmentation source type
                if "manual_masks" in pattern:
                    segmentation_type = "Manual Mask"
                elif "deep_learning_seg" in pattern:
                    segmentation_type = "deep_learning_seg Segmentation"
                break

        requirements['segmentation'] = segmentation_found
        if not segmentation_found:
            missing_files.append(QCoreApplication.translate(
                "PipelinePatientSelectionPage", "Segmentation (manual_masks/*_mask.nii[.gz] or deep_learning_seg /*_seg.nii[.gz])"))

        # --- Final eligibility decision ---
        # Patient is eligible if all required files are present
        is_eligible = all(requirements.values())

        # Return structured summary of findings
        return {
            'eligible': is_eligible,
            'requirements': requirements,
            'missing_files': missing_files,
            'segmentation_type': segmentation_type
        }

    def _load_patients(self):
        """
        Loads patient directories and builds the UI grid.

        This method:
        1. Identifies patient directories in the workspace.
        2. Verifies the eligibility of each patient via `_check_patient_requirements`.
        3. Populates the `grid_layout` with visual cards created by `_create_patient_frame`.
        4. Updates the summary statistics.
        """
        # Find all patient folders (sub-*)
        patient_dirs = self._find_patient_dirs()
        patient_dirs.sort()  # Sort alphabetically for visual consistency

        # Clear the dictionaries of buttons and patient states
        self.patient_buttons.clear()
        self.patient_status.clear()

        eligible_count = 0
        total_count = len(patient_dirs)

        # Iterate over all found patients
        for i, patient_path in enumerate(patient_dirs):
            patient_id = os.path.basename(patient_path)

            # Check the required conditions for each patient
            status = self._check_patient_requirements(patient_path, patient_id)
            self.patient_status[patient_id] = status

            # Count eligible patients
            if status['eligible']:
                eligible_count += 1

            # Create a card (frame) for the patient
            patient_frame = self._create_patient_frame(patient_id, patient_path, status)

            # Insert the card into the grid layout
            self.grid_layout.addWidget(patient_frame, i // self.column_count, i % self.column_count)

        # Update the statistical summary
        self._update_summary(eligible_count, total_count)

    def _create_patient_frame(self, patient_id, patient_path, status):
        """
        Creates a UI card (QFrame) representing a single patient.

        The card displays:
        - Patient ID and user icon.
        - Eligibility status (Green checkmark or Red cross).
        - Detailed checklist of requirements (FLAIR, Skull Strip, Segmentation).
        - A "Select" button (disabled if the patient is ineligible).

        Args:
            patient_id (str): The ID of the patient.
            patient_path (str): The file system path to the patient data.
            status (dict): The eligibility status dict returned by `_check_patient_requirements`.

        Returns:
            QFrame: The constructed patient card widget.
        """
        patient_frame = QFrame()
        patient_frame.setObjectName("patientCard")
        patient_frame.setMaximumHeight(140)  # Card height limit
        patient_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Apply different visual style based on patient eligibility
        if status['eligible']:
            frame_style = """
                QFrame#patientCard {
                    border: 2px solid #4CAF50;
                    border-radius: 10px;
                    background-color: #f0fff0;
                    padding: 10px;
                    margin: 2px;
                }
            """
        else:
            frame_style = """
                QFrame#patientCard {
                    border: 2px solid #f44336;
                    border-radius: 10px;
                    background-color: #fff0f0;
                    padding: 10px;
                    margin: 2px;
                }
            """

        patient_frame.setStyleSheet(frame_style)

        # Main horizontal layout (left → right)
        patient_layout = QHBoxLayout(patient_frame)

        # Left section: profile information
        profile_frame = QFrame()
        profile_frame.setFixedSize(150, 100)
        profile_layout = QVBoxLayout(profile_frame)
        profile_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # User image (icon)
        image = QLabel()
        pixmap = QtGui.QPixmap(resource_path("resources/user.png")).scaled(
            30, 30, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        image.setPixmap(pixmap)
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Patient ID label
        patient_label = QLabel(f"{patient_id}")
        patient_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        patient_label.setStyleSheet("font-weight: bold; font-size: 12px;")

        # Status label (Eligible / Not eligible)
        if status['eligible']:
            status_label = QLabel(QCoreApplication.translate("PipelinePatientSelectionPage", "✓ Ready for Pipeline"))
            status_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 10px;")
        else:
            status_label = QLabel(QCoreApplication.translate("PipelinePatientSelectionPage", "✗ Missing Requirements"))
            status_label.setStyleSheet("color: #f44336; font-weight: bold; font-size: 10px;")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add widgets to the profile layout
        profile_layout.addWidget(image)
        profile_layout.addWidget(patient_label)
        profile_layout.addWidget(status_label)

        # Center section: requirement details
        details_frame = QFrame()
        details_layout = QVBoxLayout(details_frame)
        details_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Status indicators for each required step
        req_indicators = []
        req_labels = {
            'flair': 'FLAIR',
            'skull_stripping': 'Skull Strip',
            'segmentation': QCoreApplication.translate("PipelinePatientSelectionPage", 'Segmentation')
        }

        # Display ✓ or ✗ next to each requirement
        for req, label in req_labels.items():
            indicator = QLabel()
            if status['requirements'][req]:
                indicator.setText(f"✓ {label}")
                indicator.setStyleSheet("color: #4CAF50; font-size: 10px; padding: 1px;")
            else:
                indicator.setText(f"✗ {label}")
                indicator.setStyleSheet("color: #f44336; font-size: 10px; padding: 1px;")
            req_indicators.append(indicator)
            details_layout.addWidget(indicator)

        # Show segmentation type if available
        if status['segmentation_type']:
            seg_type_label = QLabel(f"({status['segmentation_type']})")
            seg_type_label.setStyleSheet("color: #666666; font-size: 9px; font-style: italic;")
            details_layout.addWidget(seg_type_label)

        # Right section: selection button
        button = QPushButton(QCoreApplication.translate("PipelinePatientSelectionPage", "Select"))
        button.setCheckable(True)  # Allows to toggle selection

        if status['eligible']:
            # Style for active (eligible) button
            button.setStyleSheet("""
                QPushButton {
                    border-radius: 12px;
                    padding: 8px 16px;
                    background-color: #DADADA;
                    font-weight: bold;
                    min-width: 80px;
                }
                QPushButton:checked {
                    background-color: #4CAF50;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #c0c0c0;
                }
                QPushButton:checked:hover {
                    background-color: #45a049;
                }
            """)

            # Restore previous selection if it exists
            is_selected = patient_id in self.selected_patients
            button.setChecked(is_selected)
            button.setText(
                QCoreApplication.translate("PipelinePatientSelectionPage", "Selected")
                if is_selected else QCoreApplication.translate("PipelinePatientSelectionPage", "Select")
            )

            # Connect button click to selection handler
            button.clicked.connect(lambda checked, pid=patient_id, btn=button: self._toggle_patient(pid, checked, btn))
        else:
            # If not eligible, disable the button
            button.setText(QCoreApplication.translate("PipelinePatientSelectionPage", "Not Eligible"))
            button.setEnabled(False)
            button.setStyleSheet("""
                QPushButton {
                    border-radius: 12px;
                    padding: 8px 16px;
                    background-color: #f0f0f0;
                    color: #888888;
                    font-weight: bold;
                    min-width: 80px;
                }
            """)

        # Save reference of the button in the dictionary
        self.patient_buttons[patient_id] = button

        # Assemble all sections into the main layout
        patient_layout.addWidget(profile_frame)
        patient_layout.addWidget(details_frame)
        patient_layout.addStretch()  # Flexible space
        patient_layout.addWidget(button)

        return patient_frame

    def _update_summary(self, eligible_count, total_count):
        """
        Updates the numeric values in the summary widget.

        Args:
            eligible_count (int): Number of patients who met all requirements.
            total_count (int): Total number of patients found.
        """
        self.total_label.value_label.setText(str(total_count))
        self.eligible_label.value_label.setText(str(eligible_count))
        self.not_eligible_label.value_label.setText(str(total_count - eligible_count))

    def _select_all_eligible_patients(self):
        """
        Action handler: Automatically selects all patients marked as eligible.
        Updates the main application buttons after selection.
        """
        for patient_id, button in self.patient_buttons.items():
            if self.patient_status[patient_id]['eligible'] and not button.isChecked():
                button.setChecked(True)
                button.setText(QCoreApplication.translate("PipelinePatientSelectionPage", "Selected"))
                self.selected_patients.add(patient_id)
        # Update main app buttons
        if self.context and "update_main_buttons" in self.context:
            self.context["update_main_buttons"]()

    def _deselect_all_patients(self):
        """
        Action handler: Deselects all currently selected patients.
        Updates the main application buttons after deselection.
        """
        for patient_id, button in self.patient_buttons.items():
            if button.isChecked() and button.isEnabled():
                button.setChecked(False)
                button.setText(QCoreApplication.translate("PipelinePatientSelectionPage", "Select"))
                self.selected_patients.discard(patient_id)
        # Update main buttons
        if self.context and "update_main_buttons" in self.context:
            self.context["update_main_buttons"]()

    def _refresh_patient_status(self):
        """
        Action handler: Reloads all patients and re-verifies their status.

        This is useful if files have been added to the workspace while the
        application was open. It attempts to preserve existing selections if
        the patient remains eligible.
        """
        # Save current selections
        current_selections = self.selected_patients.copy()

        # Remove existing widgets from the grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        # Reload patients and update status
        self._load_patients()

        # Restore still-valid selections
        valid_selections = set()
        for patient_id in current_selections:
            if (patient_id in self.patient_status and
                    self.patient_status[patient_id]['eligible'] and
                    patient_id in self.patient_buttons):
                valid_selections.add(patient_id)
                button = self.patient_buttons[patient_id]
                button.setChecked(True)
                button.setText(QCoreApplication.translate("PipelinePatientSelectionPage", "Selected"))

        self.selected_patients = valid_selections

    def _toggle_patient(self, patient_id, is_selected, button):
        """
        Toggles the selection status of a single patient.

        Args:
            patient_id (str): The ID of the patient.
            is_selected (bool): The new state (True for selected).
            button (QPushButton): The button widget triggering the event.
        """
        if is_selected:
            self.selected_patients.add(patient_id)
            button.setText(QCoreApplication.translate("PipelinePatientSelectionPage", "Selected"))
        else:
            self.selected_patients.discard(patient_id)
            button.setText(QCoreApplication.translate("PipelinePatientSelectionPage", "Select"))
        # Update main buttons
        if self.context and "update_main_buttons" in self.context:
            self.context["update_main_buttons"]()

    def _find_patient_dirs(self):
        """
        Scans the workspace path for patient directories.

        It looks for directories starting with "sub-" and excludes "derivatives"
        and "pipeline" directories.

        Returns:
            list: A list of full paths to patient directories.
        """
        patient_dirs = []

        for root, dirs, files in os.walk(self.workspace_path):
            # Exclude irrelevant folders
            if "derivatives" in dirs:
                dirs.remove("derivatives")
            if "pipeline" in dirs:
                dirs.remove("pipeline")

            # Add directories starting with "sub-"
            for dir_name in dirs:
                if dir_name.startswith("sub-"):
                    full_path = os.path.join(root, dir_name)
                    patient_dirs.append(full_path)

            # Prevent going deeper into sub-* directories
            dirs[:] = [d for d in dirs if not d.startswith("sub-")]

        return patient_dirs

    def _update_column_count(self):
        """
        Recalculates the number of grid columns based on the available viewport width.

        If the calculated column count differs from the current count, the grid
        is reloaded to adjust the layout.
        """
        available_width = self.scroll_area.viewport().width() - 40
        min_card_width = 400  # Minimum width for a card

        new_column_count = max(1, available_width // min_card_width)

        # If column count changes, reload the grid
        if new_column_count != self.column_count:
            self.column_count = new_column_count
            self._reload_patient_grid()

    def _reload_patient_grid(self):
        """
        Rebuilds the patient grid (e.g., after a resize) while maintaining selections.
        """
        selected = self.selected_patients.copy()

        # Remove existing widgets
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        # Reload patients in the new layout
        self._load_patients()

        # Restore valid selections
        valid_selections = set()
        for patient_id in selected:
            if (patient_id in self.patient_status and
                    self.patient_status[patient_id]['eligible'] and
                    patient_id in self.patient_buttons):
                valid_selections.add(patient_id)
                button = self.patient_buttons[patient_id]
                button.setChecked(True)
                button.setText(QCoreApplication.translate("PipelinePatientSelectionPage", "Selected"))

        self.selected_patients = valid_selections

    def _build_pipeline_config(self):
        """
        Generates and saves a JSON file containing the initial pipeline configuration.

        This method iterates through selected patients, resolves relative paths for
        all required files (MRI, Skull-strip, PET, Masks), and detects ambiguities
        (multiple files found) which are flagged as `need_revision`.

        The configuration is saved to `workspace/pipeline/XX_config.json`, where XX
        is an auto-incrementing sequence number.

        Returns:
            str: The full path to the generated JSON configuration file.
        """
        config = {}  # Main dictionary that will store configuration data for all patients

        # Iterate over all selected patients
        for patient_id in self.selected_patients:
            patient_entry = {}  # Holds the configuration for a single patient
            need_revision = False  # Flag indicating if manual review is required due to ambiguities

            # ----------------------------------------------------
            # MRI (FLAIR)
            # ----------------------------------------------------
            flair_patterns = [
                os.path.join(self.workspace_path, patient_id, "anat", "*_flair.nii"),
                os.path.join(self.workspace_path, patient_id, "anat", "*_flair.nii.gz")
            ]
            flair_files = []
            # Search for FLAIR MRI files matching the defined patterns
            for p in flair_patterns:
                flair_files.extend(glob.glob(p))
            # If more than one FLAIR file exists, mark for manual revision
            if len(flair_files) > 1:
                need_revision = True
            # Store the relative path of the FLAIR file if found
            patient_entry["mri"] = os.path.relpath(flair_files[0], self.workspace_path) if flair_files else None

            # ----------------------------------------------------
            # MRI Skull Stripped
            # ----------------------------------------------------
            mri_str_patterns = [
                os.path.join(self.workspace_path, "derivatives", "skullstrips", patient_id, "anat", "*_brain.nii"),
                os.path.join(self.workspace_path, "derivatives", "skullstrips", patient_id, "anat", "*_brain.nii.gz")
            ]
            mri_str_files = []
            # Search for preprocessed (skull-stripped) MRI files
            for p in mri_str_patterns:
                mri_str_files.extend(glob.glob(p))
            if len(mri_str_files) > 1:
                need_revision = True
            patient_entry["mri_str"] = os.path.relpath(mri_str_files[0], self.workspace_path) if mri_str_files else None

            # ----------------------------------------------------
            # Static PET (Session 01)
            # ----------------------------------------------------
            pet_patterns = [
                os.path.join(self.workspace_path, patient_id, "ses-01", "pet", "*_pet.nii"),
                os.path.join(self.workspace_path, patient_id, "ses-01", "pet", "*_pet.nii.gz")
            ]
            pet_files = []
            # Locate static PET scans
            for p in pet_patterns:
                pet_files.extend(glob.glob(p))
            if len(pet_files) > 1:
                need_revision = True
            patient_entry["pet"] = os.path.relpath(pet_files[0], self.workspace_path) if pet_files else None

            # ----------------------------------------------------
            # Dynamic PET (4D, optional)
            # ----------------------------------------------------
            pet4d_patterns = [
                os.path.join(self.workspace_path, patient_id, "ses-02", "pet", "*_pet.nii"),
                os.path.join(self.workspace_path, patient_id, "ses-02", "pet", "*_pet.nii.gz")
            ]
            pet4d_files = []
            # Locate dynamic PET files (4D data)
            for p in pet4d_patterns:
                pet4d_files.extend(glob.glob(p))
            if len(pet4d_files) > 1:
                need_revision = True
            pet4d_file = pet4d_files[0] if pet4d_files else None
            patient_entry["pet4d"] = os.path.relpath(pet4d_files[0], self.workspace_path) if pet4d_files else None

            # ----------------------------------------------------
            # PET JSON sidecar (metadata for dynamic PET)
            # ----------------------------------------------------
            pet_json_file = None
            if pet4d_file:
                # Derive the expected .json filename from the PET file prefix
                basename = os.path.basename(pet4d_file)
                stem_no_ext = basename.split('.')[0]
                candidate = os.path.join(os.path.dirname(pet4d_file), stem_no_ext + '.json')
                if os.path.exists(candidate):
                    pet_json_file = candidate
            # Store relative path to PET JSON file if it exists
            patient_entry["pet4d_json"] = os.path.relpath(pet_json_file, self.workspace_path) if pet_json_file else None

            # ----------------------------------------------------
            # Tumor MRI Mask (manual or automated)
            # ----------------------------------------------------
            tumor_patterns = [
                # Manual segmentation masks
                os.path.join(self.workspace_path, "derivatives", "manual_masks", patient_id, "anat", "*_mask.nii"),
                os.path.join(self.workspace_path, "derivatives", "manual_masks", patient_id, "anat", "*_mask.nii.gz"),
                # Deep learning-based segmentations
                os.path.join(self.workspace_path, "derivatives", "deep_learning_seg", patient_id, "anat",
                             "*_seg.nii"),
                os.path.join(self.workspace_path, "derivatives", "deep_learning_seg", patient_id, "anat",
                             "*_seg.nii.gz")
            ]
            tumor_files = []
            # Search for tumor mask files
            for p in tumor_patterns:
                tumor_files.extend(glob.glob(p))
            if len(tumor_files) > 1:
                need_revision = True
            patient_entry["tumor_mri"] = os.path.relpath(tumor_files[0], self.workspace_path) if tumor_files else None

            # Add the final review flag to indicate if manual review is needed
            patient_entry["need_revision"] = need_revision

            # Store the patient's configuration in the main config dictionary
            config[patient_id] = patient_entry

        # ----------------------------------------------------
        # Create and save the pipeline configuration JSON file
        # ----------------------------------------------------
        pipeline_dir = os.path.join(self.workspace_path, "pipeline")

        # Create the 'pipeline' directory if it doesn't exist
        if not os.path.exists(pipeline_dir):
            os.makedirs(pipeline_dir)
            log.info(f"Created pipeline directory: {pipeline_dir}")

        # Determine the next sequential ID number (e.g., 01, 02, 03, ...)
        config_id = self._get_next_config_id(pipeline_dir)

        # Build the filename using the sequential ID
        filename = f"{config_id:02d}_config.json"
        output_path = os.path.join(pipeline_dir, filename)

        # Save the configuration dictionary as a formatted JSON file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        # Log the output path for reference
        log.info(f"Pipeline configuration saved to: {output_path}")

        # Return the full path to the generated configuration file
        return output_path

    def _get_next_config_id(self, pipeline_dir):
        """
        Finds the next available sequential numeric ID for configuration files.

        This method scans the pipeline directory for existing configuration files
        matching `*_config.json`, extracts their numeric prefixes, and determines
        the next sequence number.

        Args:
            pipeline_dir (str): Path to the pipeline directory where config files are stored.

        Returns:
            int: The next available numeric ID for a new configuration file.
        """
        # Pattern used to search for existing pipeline configuration files
        config_pattern = os.path.join(pipeline_dir, "*_config.json")
        existing_configs = glob.glob(config_pattern)

        # If no config files exist, start numbering from 1
        if not existing_configs:
            return 1

        existing_ids = []  # Stores all numeric IDs extracted from existing filenames

        # Iterate through all existing config files to extract their numeric IDs
        for config_file in existing_configs:
            filename = os.path.basename(config_file)  # Example: "12_config.json"
            try:
                # Extract the numeric part before "_config.json"
                id_str = filename.split("_")[0]  # → "12"
                config_id = int(id_str)  # Convert to integer
                existing_ids.append(config_id)
            except (ValueError, IndexError):
                # Skip any files that don't follow the expected naming format
                continue

        # If no valid numeric IDs were found, default to 1
        if not existing_ids:
            return 1

        # Return the next sequential ID (maximum existing + 1)
        return max(existing_ids) + 1

    def on_enter(self):
        """
        Triggered when the application navigates to this page.
        Refreshes the patient status to ensure file availability is up to date.
        """
        self._refresh_patient_status()

    def is_ready_to_advance(self):
        """
        Checks if the user can proceed to the next page.

        Returns:
            bool: True if at least one patient has been selected, False otherwise.
        """
        return len(self.selected_patients) > 0

    def is_ready_to_go_back(self):
        """
        Checks if the user can navigate back to the previous page.

        Returns:
            bool: Always True for this page.
        """
        return True

    def next(self, context):
        """
        Proceeds to the next page in the workflow.

        This method builds the pipeline configuration file based on the selection
        and initializes the `PipelineReviewPage`.

        Args:
            context (dict): The application context.

        Returns:
            Page: The instance of the next page to be displayed.
        """
        # Generate a new pipeline configuration file before continuing
        self._build_pipeline_config()

        # If a next page already exists, reuse it
        if self.next_page:
            self.next_page.on_enter()
            return self.next_page
        else:
            # Otherwise, create a new review page and register it in navigation history
            self.next_page = PipelineReviewPage(context, self)
            self.context["history"].append(self.next_page)
            self.next_page.on_enter()
            return self.next_page

    def back(self):
        """
        Navigates back to the previous page.

        Returns:
            Page: The previous page instance, or None if no previous page exists.
        """
        if self.previous_page:
            self.previous_page.on_enter()
            return self.previous_page
        return None

    def get_selected_patients(self):
        """
        Retrieves the IDs of all currently selected patients.

        Returns:
            list: A list of strings representing patient IDs.
        """
        return list(self.selected_patients)

    def get_eligible_patients(self):
        """
        Retrieves the IDs of all patients marked as eligible.

        Returns:
            list: A list of strings representing eligible patient IDs.
        """
        return [pid for pid, status in self.patient_status.items() if status['eligible']]

    def get_patient_status_summary(self):
        """
        Calculates a statistical summary of patient eligibility.

        Returns:
            dict: A dictionary containing:
                - 'total': Total number of patients scanned.
                - 'eligible': Number of patients meeting requirements.
                - 'selected': Number of currently selected patients.
                - 'not_eligible': Number of patients missing requirements.
        """
        total = len(self.patient_status)  # Count total patients being tracked
        eligible = len([s for s in self.patient_status.values() if s['eligible']])  # Count eligible ones
        selected = len(self.selected_patients)  # Count selected patients

        # Return a dictionary summarizing all relevant counts
        return {
            'total': total,
            'eligible': eligible,
            'selected': selected,
            'not_eligible': total - eligible
        }

    def reset_page(self):
        """
        Resets the page to its initial state.

        This clears the grid, selections, and internal status data, then re-scans
        the workspace for patients.
        """
        # Clear all widgets from the grid layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)  # Detach widget from layout
                widget.deleteLater()  # Schedule for deletion

        # Reset all patient-related states
        self.selected_patients.clear()  # Clear selected patients
        self.patient_buttons.clear()  # Clear patient button references
        self.patient_status.clear()  # Clear patient status dictionary

        # Reload all patient data from the workspace
        self._load_patients()

    def resizeEvent(self, event):
        """
        Handles window resize events to make the UI responsive.

        Adjusts the number of columns in the grid, font sizes, and button padding
        based on the window height and width.

        Args:
            event (QResizeEvent): The resize event.
        """
        super().resizeEvent(event)

        # Update column count dynamically based on width
        self._update_column_count()

        height = self.height()  # Current window height

        # Adjust UI style dynamically for small or large window height
        if height < 500:
            # Compact layout for small windows
            self.title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px;")
            btn_padding = "5px 10px"
            font_size_btn = 11
            max_pill_height = 70
            font_size_title = 12
            font_size_value = 14
            font_size_label = 10
            max_pill_height = 60
        else:
            # Normal layout for larger windows
            self.title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
            btn_padding = "10px 20px"
            font_size_btn = 13
            font_size_title = 16
            font_size_value = 20
            font_size_label = 13
            max_pill_height = 100

        # Update button styles dynamically
        for btn in self.buttons:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #e0e0e0;
                    padding: {btn_padding};
                    border-radius: 10px;
                    border: 1px solid #bdc3c7;
                    font-weight: bold;
                    font-size: {font_size_btn}px;
                    margin: 2px;
                }}
                QPushButton:hover {{
                    background-color: #d0d0d0;
                }}
                QPushButton:disabled {{
                    background-color: #f0f0f0;
                    color: #888888;
                }}
            """)

        # Update summary title styling
        self.title_summary.setStyleSheet(
            f"font-size: {font_size_title}px; font-weight: bold; color: #000000; margin-bottom: 8px;"
        )

        # Update pill-style status indicators (total, eligible, not eligible)
        for pill in [self.total_label, self.eligible_label, self.not_eligible_label]:
            pill.label.setStyleSheet(f"font-size: {font_size_label}px; font-weight: bold;")
            pill.value_label.setStyleSheet(
                f"font-size: {font_size_value}px; font-weight: bold; color: {pill.value_label.palette().color(pill.value_label.foregroundRole()).name()};"
            )
            pill.setMaximumHeight(max_pill_height)  # Limit vertical space

    def _translate_ui(self):
        """
        Translates all UI text elements to the current language.

        Updates labels and buttons with localized strings using Qt's translation system.
        Triggers a patient list reload to refresh status texts within patient cards.
        """
        # Set translated texts for main title and control buttons
        self.title.setText(
            QCoreApplication.translate("PipelinePatientSelectionPage", "Select Patients for Pipeline Analysis"))
        self.select_eligible_btn.setText(
            QCoreApplication.translate("PipelinePatientSelectionPage", "Select All Eligible"))
        self.deselect_all_btn.setText(QCoreApplication.translate("PipelinePatientSelectionPage", "Deselect All"))
        self.refresh_btn.setText(QCoreApplication.translate("PipelinePatientSelectionPage", "Refresh Status"))
        self.title_summary.setText(
            QCoreApplication.translate("PipelinePatientSelectionPage", "Pipeline Requirements Summary"))

        # Set translated labels for patient status summary
        self.total_label.label.setText(QCoreApplication.translate("PipelinePatientSelectionPage", "Total Patients"))
        self.eligible_label.label.setText(QCoreApplication.translate("PipelinePatientSelectionPage", "Eligible"))
        self.not_eligible_label.label.setText(
            QCoreApplication.translate("PipelinePatientSelectionPage", "Not Eligible"))

        # Reload patient list after updating UI text
        self._load_patients()