import sys
import csv
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt

class WatchListApp(QMainWindow):
    def __init__(self):
        #setup main window
        super().__init__()
        self.setWindowTitle("WatchList")
        self.resize(800, 400)
        self.central = QWidget()
        self.setCentralWidget(self.central)

        #setup layout for left side
        self.layout = QHBoxLayout(self.central)

        #setup table
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self.on_cell_clicked)
        self.table.verticalHeader().setVisible(False)  # Hide index column
        self.layout.addWidget(self.table)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        #setup layout for right side
        self.side_panel = QVBoxLayout()
        self.layout.addLayout(self.side_panel)

        #edit selected cell section
        self.edit_label = QLabel("Edit Selected Cell:")
        self.side_panel.addWidget(self.edit_label)
        self.edit_box = QLineEdit()
        self.edit_box.setEnabled(False)
        self.side_panel.addWidget(self.edit_box)
        self.save_btn = QPushButton("Save Change")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_cell_edit)
        self.side_panel.addWidget(self.save_btn)

        #remove selected show button
        self.remove_btn = QPushButton("Remove Selected Show")
        self.remove_btn.setEnabled(False)
        self.remove_btn.clicked.connect(self.remove_selected_show)
        self.side_panel.addWidget(self.remove_btn)

        #add new show section
        self.add_label = QLabel("Add New Show")
        self.side_panel.addWidget(self.add_label)
        self.add_show_name = QLineEdit()
        self.add_show_name.setPlaceholderText("Show Name")
        self.side_panel.addWidget(self.add_show_name)
        self.add_episode_number = QLineEdit()
        self.add_episode_number.setPlaceholderText("Episode Number (whole number)")
        self.side_panel.addWidget(self.add_episode_number)
        self.add_watch_status = QLineEdit()
        self.add_watch_status.setPlaceholderText("Watch Status")
        self.side_panel.addWidget(self.add_watch_status)
        self.add_btn = QPushButton("Add Show")
        self.add_btn.clicked.connect(self.add_new_show)
        self.side_panel.addWidget(self.add_btn)
        self.side_panel.addStretch()

        #open and save CSV buttons in bottom corner
        btn_row = QHBoxLayout()
        self.open_btn = QPushButton("Open CSV")
        self.open_btn.clicked.connect(self.open_csv)
        btn_row.addWidget(self.open_btn, stretch=1)
        self.save_btn_csv = QPushButton("Save CSV")
        self.save_btn_csv.clicked.connect(self.save_csv)
        btn_row.addWidget(self.save_btn_csv, stretch=1)
        self.side_panel.addLayout(btn_row)

        #nothing is selected initially
        self.selected_row = None
        self.selected_col = None

    #open CSV file if formatted right and remove duplicates
    def open_csv(self):
        #open file
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{e}")
            return
        #validate header
        if not rows or rows[0] != ["Show Name", "Episode Number", "Watch Status"]:
            QMessageBox.critical(self, "Invalid Format", "CSV header must be: Show Name,Episode Number,Watch Status")
            return
        #validate rows
        for i, row in enumerate(rows[1:], start=2):
            if len(row) != 3:
                QMessageBox.critical(self, "Invalid Format", f"Row {i} does not have 3 columns.")
                return

        #remove exact duplicates (keep first one, same showname is allowed just not exact same episode count and status)
        seen = set()
        unique_rows = [rows[0]]
        for row in rows[1:]:
            key = tuple(row)
            if key not in seen:
                seen.add(key)
                unique_rows.append(row)
        self.populate_table(unique_rows)

    #load the given rows into the table widget
    def populate_table(self, rows):
        self.table.clear()
        self.table.setRowCount(len(rows) - 1)
        self.table.setColumnCount(3)
        #ensure "Show Name" is a column header
        self.table.setHorizontalHeaderLabels(["Show Name", "Episode Number", "Watch Status"])
        for r, row in enumerate(rows[1:]):
            for c, val in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(val))
        self.table.resizeColumnsToContents()
        self.selected_row = None
        self.selected_col = None
        self.edit_box.setText("")
        self.edit_box.setEnabled(False)
        self.save_btn.setEnabled(False)

    #handle cell clicks
    def on_cell_clicked(self, row, col):
        item = self.table.item(row, col)
        if item:
            self.selected_row = row
            self.selected_col = col
            self.edit_box.setText(item.text())
            self.edit_box.setEnabled(True)
            self.save_btn.setEnabled(True)
            self.remove_btn.setEnabled(True)
        else:
            self.remove_btn.setEnabled(False)

    #save new edited value to cell
    def save_cell_edit(self):
        if self.selected_row is not None and self.selected_col is not None:
            new_val = self.edit_box.text()
            self.table.setItem(self.selected_row, self.selected_col, QTableWidgetItem(new_val))

    #remove current selected show from table
    def remove_selected_show(self):
        if self.selected_row is not None:
            self.table.removeRow(self.selected_row)
            self.selected_row = None
            self.selected_col = None
            self.edit_box.setText("")
            self.edit_box.setEnabled(False)
            self.save_btn.setEnabled(False)
            self.remove_btn.setEnabled(False)

    #add new show to the table
    def add_new_show(self):
        #if table is empty (no CSV loaded), initialize headers and table
        if self.table.rowCount() == 0 and self.table.columnCount() == 0:
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["Show Name", "Episode Number", "Watch Status"])
            self.table.verticalHeader().setVisible(False)
            self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        #add show
        name = self.add_show_name.text().strip()
        episode = self.add_episode_number.text().strip()
        status = self.add_watch_status.text().strip()
        if not name or not episode or not status:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return
        try:
            episode_int = int(episode)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Episode Number must be an integer (whole number).")
            return
        #check for duplicates (all 3 fields must match exactly)
        for row in range(self.table.rowCount()):
            n = self.table.item(row, 0)
            e = self.table.item(row, 1)
            s = self.table.item(row, 2)
            if n and e and s:
                if (
                    n.text().strip() == name and
                    e.text().strip() == str(episode_int) and
                    s.text().strip() == status
                ):
                    QMessageBox.warning(self, "Duplicate Entry", "This show already exists in the list.")
                    return
        #insert new row
        row_pos = self.table.rowCount()
        self.table.insertRow(row_pos)
        self.table.setItem(row_pos, 0, QTableWidgetItem(name))
        self.table.setItem(row_pos, 1, QTableWidgetItem(str(episode_int)))
        self.table.setItem(row_pos, 2, QTableWidgetItem(status))
        self.table.resizeColumnsToContents()
        self.add_show_name.clear()
        self.add_episode_number.clear()
        self.add_watch_status.clear()

    #saves the current table data to a CSV file
    def save_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        #ensure file has .csv extension
        if not path.lower().endswith('.csv'):
            path += '.csv'
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                #write header
                writer.writerow(["Show Name", "Episode Number", "Watch Status"])
                #write table rows
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")

#actually load app
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WatchListApp()
    win.show()
    sys.exit(app.exec())
