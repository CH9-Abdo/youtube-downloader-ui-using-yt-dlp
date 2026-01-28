import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QRadioButton, QButtonGroup, QTextEdit, QFileDialog,
                             QComboBox, QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont


class DownloadThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, url, download_type, output_path, video_format=None, audio_format=None, quality=None):
        super().__init__()
        self.url = url
        self.download_type = download_type
        self.output_path = output_path
        self.video_format = video_format
        self.audio_format = audio_format
        self.quality = quality
        
    def run(self):
        try:
            output_template = os.path.join(self.output_path, "%(title)s.%(ext)s")
            
            if self.download_type == "video":
                # Build video download command
                command = f'yt-dlp -o "{output_template}"'
                
                # Add format/quality options
                if self.quality == "best":
                    command += ' -f "bestvideo+bestaudio/best"'
                elif self.quality == "720p":
                    command += ' -f "bestvideo[height<=720]+bestaudio/best[height<=720]"'
                elif self.quality == "480p":
                    command += ' -f "bestvideo[height<=480]+bestaudio/best[height<=480]"'
                elif self.quality == "360p":
                    command += ' -f "bestvideo[height<=360]+bestaudio/best[height<=360]"'
                
                # Add video format conversion if needed
                if self.video_format and self.video_format != "default":
                    command += f' --recode-video {self.video_format}'
                
                command += f' "{self.url}"'
                
            else:  # audio
                command = f'yt-dlp -x --audio-format {self.audio_format} -o "{output_template}" "{self.url}"'
                
                # Add audio quality
                if self.quality:
                    command += f' --audio-quality {self.quality}'
            
            self.progress.emit(f"Running command: {command}\n")
            
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                self.progress.emit(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                self.finished.emit(True, "Download completed successfully!")
            else:
                self.finished.emit(False, f"Command failed with return code: {process.returncode}")
                
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")


class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.download_thread = None
        
    def initUI(self):
        self.setWindowTitle('YouTube Downloader - Advanced')
        self.setGeometry(100, 100, 800, 700)
        
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
        self.path_input.setText(os.path.expanduser('~/Videos'))
        self.path_input.setFont(QFont('Arial', 10))
        self.browse_btn = QPushButton('Browse')
        self.browse_btn.setFont(QFont('Arial', 10))
        self.browse_btn.clicked.connect(self.browse_folder)
        
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        layout.addLayout(path_layout)
        
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
        layout.addWidget(self.download_btn)
        
        # Progress/Status area
        status_label = QLabel('Status:')
        status_label.setFont(QFont('Arial', 10, QFont.Bold))
        layout.addWidget(status_label)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setFont(QFont('Courier', 9))
        self.status_text.setMaximumHeight(150)
        layout.addWidget(self.status_text)
        
        central_widget.setLayout(layout)
    
    def on_type_changed(self):
        is_video = self.video_radio.isChecked()
        self.video_options_group.setVisible(is_video)
        self.audio_options_group.setVisible(not is_video)
        
        # Update default path
        if is_video:
            self.path_input.setText(os.path.expanduser('~/Videos'))
        else:
            self.path_input.setText(os.path.expanduser('~/Music'))
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.path_input.setText(folder)
    
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
            except:
                QMessageBox.warning(self, 'Warning', 'Could not create output directory!')
                return
        
        download_type = "video" if self.video_radio.isChecked() else "audio"
        
        # Get options
        video_format = None
        audio_format = None
        quality = None
        
        if download_type == "video":
            quality_map = {'Best': 'best', '720p': '720p', '480p': '480p', '360p': '360p'}
            quality = quality_map[self.video_quality_combo.currentText()]
            
            video_format_text = self.video_format_combo.currentText().lower()
            if video_format_text != 'default':
                video_format = video_format_text
        else:
            audio_format = self.audio_format_combo.currentText()
            
            quality_map = {'Best (0)': '0', 'High (2)': '2', 'Medium (5)': '5', 'Low (9)': '9'}
            quality = quality_map[self.audio_quality_combo.currentText()]
        
        self.download_btn.setEnabled(False)
        self.status_text.clear()
        self.status_text.append(f"Starting download...")
        self.status_text.append(f"URL: {url}")
        self.status_text.append(f"Type: {download_type.upper()}")
        self.status_text.append(f"Output: {output_path}\n")
        
        self.download_thread = DownloadThread(url, download_type, output_path, video_format, audio_format, quality)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()
    
    def update_progress(self, message):
        self.status_text.append(message)
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )
    
    def download_finished(self, success, message):
        self.status_text.append(f"\n{message}")
        self.download_btn.setEnabled(True)
        
        if success:
            QMessageBox.information(self, 'Success', message)
        else:
            QMessageBox.critical(self, 'Error', message)


def main():
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()