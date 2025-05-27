from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QGridLayout,
    QFileDialog,
    QTextEdit,
    QLineEdit,
    QCheckBox,
    QSizePolicy
)
from PySide6.QtCore import Qt
import pyqtgraph as pg
import pyqtgraph.colormap as pcm
import numpy as np
from dataAnalyzer import DataAnalyzer

class DataSuite(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Data Analytics Suite")
        self.setGeometry(150, 150, 1100, 200)
        self.setStyleSheet("background-color: #111111")
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(10,0,10,0)
        self.title_layout = QHBoxLayout()
        self.title_layout.setSpacing(0)
        
        self.title = QLabel("Data Analytics Suite")
        self.title.setFixedHeight(80)
        self.title.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # Custom size policy
        self.title.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.title.setStyleSheet("font-size: 50px; margin-top: 10px; margin-bottom: 0px; padding: 0px;")
        self.title_layout.addWidget(self.title, stretch=0)
        self.main_layout.addLayout(self.title_layout, stretch=0)
        
        self.col_layout = QHBoxLayout()
        self.col_layout.setSpacing(0)
        
        ###########
        ## START OF FIRST COL
        ###########
        
        self.first_col = QVBoxLayout()
        
        self.load_data_label = QLabel("Load Data")

        self.load_data_label.setStyleSheet("font-size: 26px; margin-bottom: 10px; padding: 2px; border-bottom: 2px solid #fff")
        self.load_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.file_path_label = QLabel("No File Selected")
        self.file_path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_path_label.setStyleSheet("font-size: 14px; margin-top: 10px; margin-bottom: 10px;")
        
        self.file_button = QPushButton("Select a File")
        self.file_button.setStyleSheet(
        """
        QPushButton {
            background-color: #0078D7;
            margin-top: 10px;
            border-radius: 8px;
            padding: 8px;
            color: white;
            font-size: 15px;
        }
        QPushButton:hover {
            background-color: #005FA3;
        }
        QPushButton:pressed {
            background-color: #004080
        }
        """
        )
        self.file_button.clicked.connect(self.open_file_dialog)
        
        self.file_note = QLabel('File should have columns named \n \"Time (min)\", \"IS\", \"Marker\", and each isomer should begin with \"Isomer\".')
        self.file_note.setStyleSheet("font-style: italic; font-size: 12px; margin-bottom: 10px; margin-top: 10px;")
        self.file_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.grid_info_layout = QGridLayout()
        self.grid_info_layout.setSpacing(1)
        self.grid_info_layout.setContentsMargins(10, 5, 10, 5)
        self.col_text = QLabel("Number of Columns")
        self.row_text = QLabel("Number of Rows")
        self.num_droplets = QLabel("Droplets per Sample")
        self.col_input = QLineEdit()
        self.row_input = QLineEdit()
        self.droplets_input = QLineEdit()
        self.col_input.setFixedWidth(25)
        self.row_input.setFixedWidth(25)
        self.droplets_input.setFixedWidth(25)
        self.row_input.setStyleSheet("QLineEdit"
                                "{"
                                "background : gray;"
                                "}")
        self.col_input.setStyleSheet("QLineEdit"
                                "{"
                                "background : gray;"
                                "}") 
        self.droplets_input.setStyleSheet("QLineEdit"
                                "{"
                                "background : gray;"
                                "}") 
        
        self.marker_checkbox_label = QLabel("Marker Present?")
        self.desired_heatmap_iso_label = QLabel("Name of Isomer for Heatmap (as named in input file)")
        self.marker_checkbox_label.setStyleSheet("margin-top: 20px; padding: 0px; margin-right: 5px;")
        self.desired_heatmap_iso_label.setStyleSheet("margin-top: 20px; padding: 0px; margin-right: 5px;")
        self.desired_heatmap_iso = QLineEdit()
        self.desired_heatmap_iso.setStyleSheet("QLineEdit"
            "{"
                "margin-top: 20px;"
                "background : gray;"
            "}") 
        self.desired_heatmap_iso.setFixedWidth(200)
        self.marker_checkbox = QCheckBox()
        self.marker_checkbox.setStyleSheet(
            "QCheckBox"
            "{"
            "background-color: white;"
            "margin-top: 20px;"
            "padding-left: 0px;"
            "margin-left: 0px;"
            "}"
            "QCheckBox::pressed"
            "{"
            "background-color: gray"
            "}"
            "QCheckBox::checked"
            "{"
            "background-color: darkgray"
            "}"
        )
        self.marker_checkbox.setFixedWidth(18)
        
        self.grid_info_layout.addWidget(self.row_text, 0, 0)
        self.grid_info_layout.addWidget(self.col_text, 1, 0)
        self.grid_info_layout.addWidget(self.num_droplets, 2, 0)
        self.grid_info_layout.addWidget(self.marker_checkbox_label, 3, 0)
        self.grid_info_layout.addWidget(self.desired_heatmap_iso_label, 4, 0)
        
        self.grid_info_layout.addWidget(self.row_input, 0, 1)
        self.grid_info_layout.addWidget(self.col_input, 1, 1)
        self.grid_info_layout.addWidget(self.droplets_input, 2, 1)
        self.grid_info_layout.addWidget(self.marker_checkbox, 3, 1)
        self.grid_info_layout.addWidget(self.desired_heatmap_iso, 4, 1)
        
        for row in range(5):
            for col in range(2):
                item = self.grid_info_layout.itemAtPosition(row, col)
                if item is not None:
                    widget = item.widget()
                    if widget:
                        widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        self.first_col_spacer = QWidget()
        self.first_col_spacer.setFixedHeight(215)
        
        self.first_col.addWidget(self.load_data_label)
        self.first_col.addWidget(self.file_path_label)
        self.first_col.addWidget(self.file_button)
        self.first_col.addWidget(self.file_note)
        self.first_col.addLayout(self.grid_info_layout)
        self.first_col.addWidget(self.first_col_spacer)
        ##########
        ## END OF FIRST COL START OF SECOND COL
        ##########
        
        self.second_col = QVBoxLayout()
                
        self.generate_label = QLabel("Generate Results")
        self.generate_label.setStyleSheet("font-size: 26px; margin-bottom: 10px; padding: 2px; border-bottom: 2px solid #fff")
        self.generate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.output_file_name = QTextEdit("Output File Name")
        self.output_file_name.setFixedHeight(30)
        
        self.output_folder_label = QLabel("No Folder Selected")
        self.output_folder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.output_folder_label.setStyleSheet("font-size: 14px; margin-top: 10px; margin-bottom: 10px;")
        
        self.output_folder_button = QPushButton("Select an Output Folder")
        self.output_folder_button.setStyleSheet(
        """
        QPushButton {
            background-color: #0078D7;
            margin-top: 10px;
            border-radius: 8px;
            padding: 8px;
            color: white;
            font-size: 15px;
        }
        QPushButton:hover {
            background-color: #005FA3;
        }
        QPushButton:pressed {
            background-color: #004080
        }
        """
        )
        
        self.output_folder_button.clicked.connect(self.open_folder_dialog)
        
        self.generate_button = QPushButton("Generate")
        self.generate_button.setStyleSheet(
        """
        QPushButton {
            background-color: #0078D7;
            margin-top: 10px;
            border-radius: 8px;
            padding: 8px;
            color: white;
            font-size: 15px;
        }
        QPushButton:hover {
            background-color: #005FA3;
        }
        QPushButton:pressed {
            background-color: #004080
        }
        """
        )
        self.generate_button.clicked.connect(self.generate_results)
        self.heatmap_spacer = QWidget()
        self.heatmap_spacer.setFixedHeight(20)
        self.second_col_spacer = QWidget()
        self.second_col_spacer.setFixedHeight(20)
        self.view = pg.GraphicsLayoutWidget()
        self.view.setFixedSize(400, 300)
        self.view.setStyleSheet("margin-bottom: 0px; padding-bottom: 0px;")
        
        self.second_col.addWidget(self.generate_label)
        self.second_col.addWidget(self.output_file_name)
        self.second_col.addWidget(self.output_folder_label)
        self.second_col.addWidget(self.output_folder_button)
        self.second_col.addWidget(self.generate_button)
        self.second_col.addWidget(self.heatmap_spacer)
        self.second_col.addWidget(self.view)
        self.second_col.addWidget(self.second_col_spacer)
        
        self.spacer = QWidget()
        self.spacer.setFixedHeight(5)
        
        self.apply_size_policy_to_layout(self.first_col)
        self.apply_size_policy_to_layout(self.second_col)
        self.apply_size_policy_to_layout(self.col_layout)

        
        self.col_layout.addLayout(self.first_col)
        self.col_layout.addLayout(self.second_col)
        
        self.main_layout.addLayout(self.col_layout, stretch=2)
        #self.main_layout.addWidget(self.spacer)
        self.central_widget.setLayout(self.main_layout)
        self.central_widget.setStyleSheet("QWidget {color: white; }")
 
        
    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder_path:
            self.output_folder_label.setText(folder_path)
               
    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*);;Text Files (*.txt);;Python Files (*.py)"
        )
        if file_path:
            self.file_path_label.setText(file_path)

    def apply_size_policy_to_layout(self, layout, size_policy=(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)):
        for i in range(layout.count()):
            item = layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                widget.setSizePolicy(*size_policy)
        
                
    def generate_results(self):
        file_path = self.file_path_label.text()
        output_folder = self.output_folder_label.text()
        num_rows = int(self.row_input.text())
        num_cols = int(self.col_input.text())
        num_droplets = int(self.droplets_input.text())
        marker_present = self.marker_checkbox.isChecked()
        output_filename = self.output_file_name.toPlainText()
        heatmap_iso_name = self.desired_heatmap_iso.text()
        da = DataAnalyzer()
        da.run_all(file_path, marker_present, num_rows, 
                   num_cols, num_droplets, output_folder, output_filename)
        if marker_present and heatmap_iso_name != "":
            arr_2d = da.create_heatmap_array(num_rows, num_cols, num_droplets, "Isomer " + heatmap_iso_name)
            self.view.clear()
            self.plot = self.view.addPlot()
            self.img = pg.ImageItem(arr_2d)
            color_map = pcm.getFromMatplotlib('gray')
            self.img.setLookupTable(color_map.getLookupTable())
            self.plot.addItem(self.img)
            self.plot.invertY(True)
        


if __name__ == "__main__":
    app = QApplication([])
    window = DataSuite()
    window.show()
    app.exec()
