import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                           QWidget, QVBoxLayout, QHBoxLayout, QFrame)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl, QSize, QPoint, QSettings
from PyQt5.QtGui import QColor, QPalette, QFont

class FloatingButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #8B4513;
                color: #FFE4B5;
                border: 2px solid #4A2400;
                border-radius: 3px;
                padding: 3px;
                font-family: 'Medieval';
                font-size: 10px;
                min-width: 40px;
                max-width: 40px;
                min-height: 20px;
                max-height: 20px;
            }
            QPushButton:hover {
                background-color: #A0522D;
            }
        """)
        self._mousePressPos = None
        self._mousePressDelta = None
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mousePressPos = event.globalPos()
            self._mousePressDelta = self.window().pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._mousePressPos:
            delta = event.globalPos() - self._mousePressPos
            self.window().move(self._mousePressDelta + delta)
            # Save the new position whenever the window is moved
            self.window().save_window_position()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mousePressPos = None
        super().mouseReleaseEvent(event)

class DraggableWebView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._mousePressPos = None
        self._mousePressDelta = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mousePressPos = event.globalPos()
            self._mousePressDelta = self.window().pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._mousePressPos is not None:
            delta = event.globalPos() - self._mousePressPos
            self.window().move(self._mousePressDelta + delta)
            # Save the new position whenever the window is moved
            self.window().save_window_position()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mousePressPos = None
        super().mouseReleaseEvent(event)

class WebViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('PQDI', 'WebViewer')
        self.website_loaded = False
        self.expanded_size = QSize(1000, 600)
        self.collapsed_size = QSize(200, 60)
        self.base_url = "https://www.pqdi.cc/spells"
        self._mousePressPos = None
        self._mousePressDelta = None
        self.initUI()
        self.restore_window_position()

    def save_window_position(self):
        self.settings.setValue('window_position', self.pos())
        self.settings.setValue('window_state', self.website_loaded)

    def restore_window_position(self):
        position = self.settings.value('window_position')
        if position:
            self.move(position)
        
        # Optionally restore the window state (expanded/collapsed)
        was_expanded = self.settings.value('window_state', False, type=bool)
        if was_expanded:
            self.toggle_website()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mousePressPos = event.globalPos()
            self._mousePressDelta = self.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._mousePressPos is not None:
            delta = event.globalPos() - self._mousePressPos
            self.move(self._mousePressDelta + delta)
            self.save_window_position()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mousePressPos = None
        
    def closeEvent(self, event):
        # Save position before closing
        self.save_window_position()
        super().closeEvent(event)
        
    def initUI(self):
        self.setWindowTitle('Project Quarm Database Interface')
        self.resize(self.collapsed_size)
        
        # Set window to stay on top and be frameless
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # Set window transparency
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("""
            QMainWindow {
                background: transparent;
            }
        """)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(5, 5, 5, 15)
        
        # Create button container
        self.button_container = QWidget()
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setAlignment(Qt.AlignCenter)
        self.button_layout.setSpacing(5)
        self.layout.addWidget(self.button_container)
        
        # Create Back button (initially hidden)
        self.back_button = FloatingButton("←", self)
        self.back_button.hide()
        self.back_button.clicked.connect(self.go_back)
        self.button_layout.addWidget(self.back_button)
        
        # Create main button
        self.float_button = FloatingButton("PQDI", self)
        self.button_layout.addWidget(self.float_button)
        self.float_button.clicked.connect(self.toggle_website)
        
        # Create close button
        self.close_button = FloatingButton("Close", self)
        self.button_layout.addWidget(self.close_button)
        self.close_button.clicked.connect(self.close)
        
        # Create web view with zoom
        self.web_view = DraggableWebView()
        self.web_view.setZoomFactor(0.8)
        self.web_view.setUrl(QUrl("about:blank"))
        self.web_view.hide()
        self.web_view.urlChanged.connect(self.handle_url_change)
        self.web_view.setStyleSheet("""
            QWebEngineView {
                background-color: #1e1e1e;
                border: 2px solid #4A2400;
            }
        """)
        self.layout.addWidget(self.web_view)

    def handle_url_change(self, url):
        if self.website_loaded:
            if url.toString() != self.base_url:
                self.back_button.show()
            else:
                self.back_button.hide()
        
    def go_back(self):
        self.web_view.back()
        
    def toggle_website(self):
        if not self.website_loaded:
            # Expand window and show website
            self.resize(self.expanded_size)
            self.web_view.show()
            self.web_view.setUrl(QUrl(self.base_url))
            self.float_button.setText("Hide")
            self.close_button.hide()
            self.website_loaded = True
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                    border: 2px solid #4A2400;
                }
            """)
        else:
            # Collapse window and hide website
            self.web_view.setUrl(QUrl("about:blank"))
            self.web_view.hide()
            self.resize(self.collapsed_size)
            self.float_button.setText("PQDI")
            self.back_button.hide()
            self.close_button.show()
            self.website_loaded = False
            self.setStyleSheet("""
                QMainWindow {
                    background: transparent;
                }
            """)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setOrganizationName('PQDI')
    app.setApplicationName('WebViewer')
    viewer = WebViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
