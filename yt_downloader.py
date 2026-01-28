import sys
import os
import shutil
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QRadioButton, QButtonGroup, QTextEdit, QFileDialog,
                             QComboBox, QGroupBox, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QProcess, QSettings
from PyQt5.QtGui import QFont

class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.process = None
        self.settings = QSettings("MySoft", "YouTubeDownloader")
        self.initUI()
        self.check_dependencies()
        
    def initUI(self):
        self.setWindowTitle('YouTube Downloader - Advanced')
        self.setGeometry(100, 100, 800, 750)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel('YouTube Video/Audio Downloader')
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # URL input
        url_layout = QHBoxLayout()
        url_label = QLabel('YouTube URL:')
        url_label.setFont(QFont('Arial', 10))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('Enter YouTube video URL here...')
        self.url_input.setFont(QFont('Arial', 10))
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)
        
        # Download type selection
        type_group = QGroupBox("Download Type")
        type_group.setFont(QFont('Arial', 10, QFont.Bold))
        type_layout = QVBoxLayout()
        
        self.button_group = QButtonGroup()
        
        radio_layout = QHBoxLayout()
        self.video_radio = QRadioButton('Video')
        self.video_radio.setFont(QFont('Arial', 10))
        self.video_radio.setChecked(True)
        self.video_radio.toggled.connect(self.on_type_changed)
        
        self.audio_radio = QRadioButton('Audio Only')
        self.audio_radio.setFont(QFont('Arial', 10))
        self.audio_radio.toggled.connect(self.on_type_changed)
        
        self.button_group.addButton(self.video_radio)
        self.button_group.addButton(self.audio_radio)
        
        radio_layout.addWidget(self.video_radio)
        radio_layout.addWidget(self.audio_radio)
        radio_layout.addStretch()
        type_layout.addLayout(radio_layout)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Video options group
        self.video_options_group = QGroupBox("Video Options")
        self.video_options_group.setFont(QFont('Arial', 10, QFont.Bold))
        video_options_layout = QVBoxLayout()
        
        # Video quality
        quality_layout = QHBoxLayout()
        quality_label = QLabel('Quality:')
        quality_label.setFont(QFont('Arial', 10))
        self.video_quality_combo = QComboBox()
        self.video_quality_combo.addItems(['Best', '720p', '480p', '360p'])
        self.video_quality_combo.setFont(QFont('Arial', 10))
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.video_quality_combo)
        quality_layout.addStretch()
        video_options_layout.addLayout(quality_layout)
        
        # Video format
        format_layout = QHBoxLayout()
        format_label = QLabel('Format:')
        format_label.setFont(QFont('Arial', 10))
        self.video_format_combo = QComboBox()
        self.video_format_combo.addItems(['Default', 'mp4', 'mkv', 'webm', 'avi', 'flv'])
        self.video_format_combo.setFont(QFont('Arial', 10))
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.video_format_combo)
        format_layout.addStretch()
        video_options_layout.addLayout(format_layout)
        
        self.video_options_group.setLayout(video_options_layout)
        layout.addWidget(self.video_options_group)
        
        # Audio options group
        self.audio_options_group = QGroupBox("Audio Options")
        self.audio_options_group.setFont(QFont('Arial', 10, QFont.Bold))
        self.audio_options_group.setVisible(False)
        audio_options_layout = QVBoxLayout()
        
        # Audio format
        audio_format_layout = QHBoxLayout()
        audio_format_label = QLabel('Format:')
        audio_format_label.setFont(QFont('Arial', 10))
        self.audio_format_combo = QComboBox()
        self.audio_format_combo.addItems(['mp3', 'aac', 'flac', 'wav', 'm4a', 'opus', 'vorbis'])
        self.audio_format_combo.setFont(QFont('Arial', 10))
        audio_format_layout.addWidget(audio_format_label)
        audio_format_layout.addWidget(self.audio_format_combo)
        audio_format_layout.addStretch()
        audio_options_layout.addLayout(audio_format_layout)
        
        # Audio quality
        audio_quality_layout = QHBoxLayout()
        audio_quality_label = QLabel('Quality:')
        audio_quality_label.setFont(QFont('Arial', 10))
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(['Best (0)', 'High (2)', 'Medium (5)', 'Low (9)'])
        self.audio_quality_combo.setFont(QFont('Arial', 10))
        audio_quality_layout.addWidget(audio_quality_label)
        audio_quality_layout.addWidget(self.audio_quality_combo)
        audio_quality_layout.addStretch()
        audio_options_layout.addLayout(audio_quality_layout)
        
        self.audio_options_group.setLayout(audio_options_layout)
        layout.addWidget(self.audio_options_group)
        
        # Output path selection
        path_layout = QHBoxLayout()
        path_label = QLabel('Save to:')
        path_label.setFont(QFont('Arial', 10))
        self.path_input = QLineEdit()
        
        # Restore last used path or default
        last_path = self.settings.value("last_download_path")
        if last_path and os.path.exists(last_path):
            self.path_input.setText(last_path)
        else:
            self.path_input.setText(os.path.expanduser('~/Videos'))
            
        self.path_input.setFont(QFont('Arial', 10))
        self.browse_btn = QPushButton('Browse')
        self.browse_btn.setFont(QFont('Arial', 10))
        self.browse_btn.clicked.connect(self.browse_folder)
        
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        layout.addLayout(path_layout)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Buttons Layout
        btn_layout = QHBoxLayout()
        
        # Download button
        self.download_btn = QPushButton('Download')
        self.download_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.download_btn.clicked.connect(self.start_download)
        btn_layout.addWidget(self.download_btn)
        
        # Cancel button
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel_download)
        self.cancel_btn.setEnabled(False)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        
        # Progress/Status area
        status_label = QLabel('Log Output:')
        status_label.setFont(QFont('Arial', 10, QFont.Bold))
        layout.addWidget(status_label)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setFont(QFont('Courier', 9))
        self.status_text.setMaximumHeight(150)
        layout.addWidget(self.status_text)
        
        central_widget.setLayout(layout)

    def check_dependencies(self):
        missing = []
        if not shutil.which("yt-dlp"):
            missing.append("yt-dlp")
        if not shutil.which("ffmpeg"):
            missing.append("ffmpeg")
            
        if missing:
            QMessageBox.warning(
                self, 
                "Missing Dependencies", 
                f"The following required tools were not found in your PATH:\n\n{', '.join(missing)}\n\n" \
                "Please install them to use this application."
            )
            self.download_btn.setEnabled(False)
            self.status_text.append(f"CRITICAL: Missing dependencies: {', '.join(missing)}")
    
    def on_type_changed(self):
        is_video = self.video_radio.isChecked()
        self.video_options_group.setVisible(is_video)
        self.audio_options_group.setVisible(not is_video)
        
        # Only switch default paths if user hasn't manually selected a weird one (heuristic)
        current_path = self.path_input.text()
        video_path = os.path.expanduser('~/Videos')
        music_path = os.path.expanduser('~/Music')
        
        if is_video and current_path == music_path:
            self.path_input.setText(video_path)
        elif not is_video and current_path == video_path:
            self.path_input.setText(music_path)
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", self.path_input.text())
        if folder:
            self.path_input.setText(folder)
            self.settings.setValue("last_download_path", folder)
    
    def start_download(self):
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, 'Warning', 'Please enter a YouTube URL!')
            return
        
        if not url.startswith(('http://', 'https://')):
            QMessageBox.warning(self, 'Warning', 'Please enter a valid URL!')
            return
        
        output_path = self.path_input.text().strip()
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
            except Exception as e:
                QMessageBox.warning(self, 'Warning', f'Could not create output directory!\n{str(e)}')
                return
        
        # Save last used path
        self.settings.setValue("last_download_path", output_path)

        # Prepare UI
        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.url_input.setEnabled(False)
        self.status_text.clear()
        self.progress_bar.setValue(0)
        self.status_text.append(f"Starting download...\nTarget: {output_path}")

        # Build Arguments
        args = ["--newline", "--no-colors"] # --newline essential for parsing progress
        
        # Output path and template
        args.extend(["-P", output_path])
        args.extend(["-o", "%(title)s.%(ext)s"])

        download_type = "video" if self.video_radio.isChecked() else "audio"

        if download_type == "video":
            quality_map = {'Best': 'best', '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]', '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]', '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]'}
            quality_arg = quality_map[self.video_quality_combo.currentText()]
            args.extend(["-f", quality_arg])
            
            video_format_text = self.video_format_combo.currentText().lower()
            if video_format_text != 'default':
                args.extend(["--recode-video", video_format_text])
        else:
            audio_format = self.audio_format_combo.currentText()
            args.extend(["-x", "--audio-format", audio_format])
            
            quality_map = {'Best (0)': '0', 'High (2)': '2', 'Medium (5)': '5', 'Low (9)': '9'}
            args.extend(["--audio-quality", quality_map[self.audio_quality_combo.currentText()]])

        args.append(url)

        # QProcess Setup
        self.process = QProcess()
        self.process.setProgram("yt-dlp")
        self.process.setArguments(args)
        
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        self.process.errorOccurred.connect(self.process_error)
        
        self.status_text.append(f"Executing: yt-dlp {' '.join(args)}\n")
        self.process.start()
    
    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode("utf8", errors="ignore")
        self.status_text.insertPlainText(text)
        self.status_text.ensureCursorVisible()
        
        # Parse progress
        # Look for [download] 45.6% ...
        lines = text.split('\n')
        for line in lines:
            if "[download]" in line and "%" in line:
                match = re.search(r"(\d+\.\d+)%", line)
                if match:
                    try:
                        percentage = float(match.group(1))
                        self.progress_bar.setValue(int(percentage))
                    except ValueError:
                        pass

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        text = bytes(data).decode("utf8", errors="ignore")
        self.status_text.insertPlainText(text)
        self.status_text.ensureCursorVisible()

    def cancel_download(self):
        if self.process and self.process.state() == QProcess.Running:
            self.status_text.append("\nCancelling download...")
            self.process.kill()

    def process_finished(self, exit_code, exit_status):
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.url_input.setEnabled(True)
        self.process = None
        
        if exit_status == QProcess.NormalExit and exit_code == 0:
            self.progress_bar.setValue(100)
            QMessageBox.information(self, 'Success', 'Download completed successfully!')
            self.status_text.append("\nDone.")
        elif exit_status == QProcess.CrashExit: # Killed
             self.status_text.append("\nProcess cancelled or crashed.")
             self.progress_bar.setValue(0)
        else:
            QMessageBox.critical(self, 'Error', f'Download failed with exit code {exit_code}. Check logs.')
            self.status_text.append(f"\nFailed (Code {exit_code}).")

    def process_error(self, error):
        if error == QProcess.FailedToStart:
             QMessageBox.critical(self, 'Error', 'yt-dlp failed to start. Is it installed?')
             self.reset_ui_state()

    def reset_ui_state(self):
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.url_input.setEnabled(True)
        self.process = None

def main():
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()