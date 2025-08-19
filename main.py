import sys
import os
import pandas as pd
import pymysql

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTableView,
    QTextEdit, QLabel, QStyledItemDelegate, QStyle, QStyleOptionButton,
    QSlider, QStatusBar
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QUrl, QModelIndex, Signal, QEvent
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

# --- Custom Delegate for Play Button ---
class PlayButtonDelegate(QStyledItemDelegate):
    play_button_clicked = Signal(QModelIndex)

    def paint(self, painter, option, index):
        if not (option.state & QStyle.State_Enabled) or not index.data():
            super().paint(painter, option, index)
            return

        button = QStyleOptionButton()
        button.rect = option.rect
        button.text = "Play"
        button.state = QStyle.State_Enabled
        QApplication.style().drawControl(QStyle.ControlElement.CE_PushButton, button, painter)

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            if option.rect.contains(event.pos()):
                self.play_button_clicked.emit(index)
                return True
        return False

# --- Main Application Window ---
class MainWindow(QMainWindow): # Changed from QWidget to QMainWindow
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SBS ASR Data Viewer")
        self.resize(1400, 800)

        # --- Central Widget and Main Layout ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Audio Player
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5) # Start with 50% volume

        # Left side: TableView
        table_v_layout = QVBoxLayout()
        table_label = QLabel("Database Content")
        table_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.setAlternatingRowColors(True) # Improved UI
        table_v_layout.addWidget(table_label)
        table_v_layout.addWidget(self.table_view)

        # Right side: Control Panel
        right_panel_layout = QVBoxLayout()
        self.script1_label = QLabel("Script 1 (user_0002)")
        self.script1_label.setStyleSheet("font-weight: bold;")
        self.script1_display = QTextEdit()
        self.script1_display.setReadOnly(True)
        self.script2_label = QLabel("Script 2 (user_0006)")
        self.script2_label.setStyleSheet("font-weight: bold;")
        self.script2_display = QTextEdit()
        self.script2_display.setReadOnly(True)

        # Volume Control
        volume_layout = QHBoxLayout()
        volume_label = QLabel("Volume:")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)

        right_panel_layout.addWidget(self.script1_label)
        right_panel_layout.addWidget(self.script1_display)
        right_panel_layout.addWidget(self.script2_label)
        right_panel_layout.addWidget(self.script2_display)
        right_panel_layout.addLayout(volume_layout) # Add volume slider to layout

        main_layout.addLayout(table_v_layout, 3)
        main_layout.addLayout(right_panel_layout, 2)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Load data from the database.")

        # Load data and populate table
        self.df = self.load_data_from_db()
        self.setup_table_view()

    def set_volume(self, value):
        """Sets the player volume."""
        volume = value / 100.0
        self.audio_output.setVolume(volume)
        self.status_bar.showMessage(f"Volume set to {value}%", 2000) # Temporary message

    def setup_table_view(self):
        """Sets up the table view with data, model, and delegate."""
        if self.df.empty:
            self.status_bar.showMessage("No data loaded. Displaying sample data.", 5000)
            return

        if 'action' not in self.df.columns:
            self.df['action'] = "Play"

        model = self.dataframe_to_model(self.df)
        self.table_view.setModel(model)

        action_col_index = self.df.columns.get_loc('action')
        self.play_delegate = PlayButtonDelegate(self.table_view)
        self.table_view.setItemDelegateForColumn(action_col_index, self.play_delegate)
        self.play_delegate.play_button_clicked.connect(self.play_audio_from_table)

        self.table_view.selectionModel().currentChanged.connect(self.on_row_selected)
        self.table_view.resizeColumnsToContents()
        self.table_view.setColumnWidth(action_col_index, 60) # Adjust button column width

    def load_data_from_db(self):
        """MySQL에서 데이터 읽어와서 DataFrame 반환"""
        try:
            conn = pymysql.connect(
                host="10.10.110.200",
                user="labeling",
                password="SlaBel1!",
                db="sbs_asr_datas",
                charset="utf8mb4",
                connect_timeout=5
            )
            query = """SELECT
                t1.id,
                t1.filename,
                t1.contents AS script_1,
                t2.contents AS script_2,
                CASE WHEN t1.status = t2.status THEN 'match' ELSE 'mismatch' END AS result
            FROM user_0002 AS t1
            JOIN user_0006 AS t2 ON t1.id = t2.id
            WHERE t1.status != 'd'
            AND t2.status != 'd'
            AND MOD(t1.id, 4) = 2
            LIMIT 100; -- 로딩 속도를 위해 100개로 제한
            """
            df = pd.read_sql(query, conn)
            conn.close()
            message = f"Successfully loaded {len(df)} rows from the database."
            print(message)
            self.status_bar.showMessage(message, 5000)
            return df
        except Exception as e:
            error_message = f"DB connection or query failed: {e}"
            print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n{error_message}\nDB loading failed. Displaying temporary sample data.\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            self.status_bar.showMessage("DB loading failed. Using sample data.", 5000)
            return pd.DataFrame({
                'id': [1, 2, 3],
                'filename': ['sample.mp3', 'bell.mp3', 'non_existent.mp3'],
                'script_1': ['This is a sample script 1.', 'This is a bell sound.', 'This file does not exist.'],
                'script_2': ['This is a sample script 2.', 'This is a bell sound script 2.', 'N/A'],
                'result': ['match', 'mismatch', 'match']
            })

    def dataframe_to_model(self, df: pd.DataFrame) -> QStandardItemModel:
        """DataFrame을 QStandardItemModel로 변환"""
        model = QStandardItemModel(len(df), len(df.columns))
        model.setHorizontalHeaderLabels(df.columns.tolist())

        for row in range(len(df)):
            for col_idx, col_name in enumerate(df.columns):
                value = str(df.iloc[row, col_idx])
                item = QStandardItem(value)
                if col_name != 'action':
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                model.setItem(row, col_idx, item)
        return model

    def on_row_selected(self, current, previous):
        """테이블에서 행이 선택될 때 스크립트 업데이트"""
        row_index = current.row()
        if 0 <= row_index < len(self.df):
            selected_row = self.df.iloc[row_index]
            self.script1_display.setText(selected_row.get('script_1', ''))
            self.script2_display.setText(selected_row.get('script_2', ''))

    def play_audio_from_table(self, index):
        """테이블의 'Play' 버튼 클릭 시 오디오 재생"""
        row = index.row()
        if 0 <= row < len(self.df):
            # In the original code, it was file_name. But the query aliases it to filename.
            # Let's check for both for robustness.
            file_name = self.df.iloc[row].get('filename') or self.df.iloc[row].get('file_name')

            if not file_name:
                message = f"Row {row} has no file_name."
                print(message)
                self.status_bar.showMessage(message, 3000)
                return

            possible_paths = [
                os.path.abspath(os.path.join('sbs_datasets', file_name)),
                os.path.abspath(file_name)
            ]
            
            full_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    full_path = path
                    break

            if full_path:
                print(f"Attempting to play: {full_path}")
                self.player.setSource(QUrl.fromLocalFile(full_path))
                self.player.play()
                self.status_bar.showMessage(f"Now Playing: {os.path.basename(full_path)}")
            else:
                message = f"Error: Audio file not found for '{file_name}'"
                print(message)
                self.status_bar.showMessage(message, 3000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Apply a modern style
    window = MainWindow()
    window.show()
    sys.exit(app.exec())