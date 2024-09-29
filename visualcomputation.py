import sys
import os
import io
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QTextEdit, QVBoxLayout, QHBoxLayout,
    QFileDialog, QScrollArea, QSplitter
)
from PyQt5.QtGui import QPixmap, QFont, QClipboard, QImage
from PyQt5.QtCore import Qt, QBuffer, QIODevice
from PIL import Image
from pix2tex.cli import LatexOCR
import urllib.parse
import requests
import urllib.request

# Initialize the OCR model
model = LatexOCR()
WOLFRAM_APP_ID = 'K5UYVW-A9W45HJX6Y' # Replace with your actual App ID

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Image to LaTeX Solver'
        self.left = 100
        self.top = 100
        self.width = 800
        self.height = 800
        self.initUI()
        self.captured_image = None
        self.solution = ''

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Set a larger font for the entire application
        font = QFont()
        font.setPointSize(14)
        self.setFont(font)

        # Buttons
        self.upload_btn = QPushButton('Upload Image', self)
        self.upload_btn.clicked.connect(self.upload_image)

        self.paste_btn = QPushButton('Paste Image', self)
        self.paste_btn.clicked.connect(self.paste_image)

        self.convert_btn = QPushButton('Convert to LaTeX', self)
        self.convert_btn.clicked.connect(self.convert_to_latex)

        self.solve_btn = QPushButton('Solve with Wolfram Alpha', self)
        self.solve_btn.clicked.connect(self.solve_equation)

        # Labels and Text Areas
        self.image_label = QLabel('Uploaded Image will appear here', self)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.latex_label = QLabel('Extracted LaTeX Code:', self)
        self.latex_text = QTextEdit(self)
        # Allow the user to edit the LaTeX code

        # Connect text change signal to render LaTeX preview
        self.latex_text.textChanged.connect(self.render_latex)

        # Label to display the rendered LaTeX image
        self.latex_image_label = QLabel(self)
        self.latex_image_label.setAlignment(Qt.AlignCenter)

        self.solution_label = QLabel('Solution:', self)

        # Scroll Area for Solution Images
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: white;")  # Set background to white

        self.solution_container = QWidget()
        self.solution_container.setStyleSheet("background-color: white;")
        self.solution_layout = QVBoxLayout(self.solution_container)
        self.scroll_area.setWidget(self.solution_container)

        # Error message box
        self.error_text = QTextEdit(self)
        self.error_text.setReadOnly(True)
        self.error_text.setStyleSheet("color: red; background-color: white;")
        self.error_text.hide()  # Initially hidden

        # Create a top-level vertical splitter
        v_splitter = QSplitter(Qt.Vertical)

        # First section: Buttons
        button_widget = QWidget()
        hbox = QHBoxLayout(button_widget)
        hbox.addWidget(self.upload_btn)
        hbox.addWidget(self.paste_btn)
        hbox.addWidget(self.convert_btn)
        hbox.addWidget(self.solve_btn)
        v_splitter.addWidget(button_widget)

        # Second section: Image Label
        image_widget = QWidget()
        image_layout = QVBoxLayout(image_widget)
        image_layout.addWidget(self.image_label)
        v_splitter.addWidget(image_widget)

        # Third section: LaTeX code and rendered image
        latex_widget = QWidget()
        latex_layout = QVBoxLayout(latex_widget)
        latex_layout.addWidget(self.latex_label)
        latex_layout.addWidget(self.latex_text)
        latex_layout.addWidget(self.latex_image_label)
        v_splitter.addWidget(latex_widget)

        # Fourth section: Solution
        solution_widget = QWidget()
        solution_layout = QVBoxLayout(solution_widget)
        solution_layout.addWidget(self.solution_label)
        solution_layout.addWidget(self.scroll_area)
        v_splitter.addWidget(solution_widget)

        # Fifth section: Error messages
        error_widget = QWidget()
        error_layout = QVBoxLayout(error_widget)
        error_layout.addWidget(self.error_text)
        v_splitter.addWidget(error_widget)

        # Set initial sizes (optional)
        v_splitter.setSizes([50, 200, 300, 400, 100])

        # Set the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(v_splitter)
        self.setLayout(main_layout)
        self.show()

    def upload_image(self):
        # Open a file dialog to select an image file
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "",
                                                   "Image Files (*.png *.jpg *.jpeg *.bmp)", options=options)
        if file_name:
            self.captured_image = Image.open(file_name)
            self.display_captured_image(file_name)
            self.error_text.clear()
            self.error_text.hide()
        else:
            self.image_label.setText('No image selected.')

    def paste_image(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        if mime_data.hasImage():
            qimage = clipboard.image()
            pil_image = self.qimage_to_pil_image(qimage)
            self.captured_image = pil_image
            # Display the image
            pixmap = QPixmap.fromImage(qimage)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
            self.error_text.clear()
            self.error_text.hide()
        else:
            self.error_text.setPlainText('Clipboard does not contain an image.')
            self.error_text.show()

    def qimage_to_pil_image(self, qimage):
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        qimage.save(buffer, "PNG")
        pil_im = Image.open(io.BytesIO(buffer.data()))
        return pil_im

    def display_captured_image(self, image_path):
        # Display the image in the label
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))

    def convert_to_latex(self):
        if self.captured_image:
            try:
                latex_code = model(self.captured_image)
                # Update the LaTeX text box with the extracted code
                self.latex_text.setPlainText(latex_code)
                self.error_text.clear()
                self.error_text.hide()
                # Render the LaTeX code
                self.render_latex()
            except Exception as e:
                self.latex_text.setPlainText('Error during OCR.')
                self.error_text.setPlainText(f'Error during OCR: {e}')
                self.error_text.show()
        else:
            self.latex_text.setPlainText('No image uploaded.')
            self.error_text.setPlainText('No image uploaded.')
            self.error_text.show()

    def render_latex(self):
        latex_code = self.latex_text.toPlainText()
        if not latex_code.strip():
            self.latex_image_label.clear()
            return
        try:
            # Include \dpi{200} to increase the image resolution
            # You can adjust the DPI value as needed (e.g., 150, 200, 300)
            dpi_value = 200
            # You can also include \Large, \huge, or \Huge to increase font size
            size_command = r'\huge'
            # Combine the commands with the LaTeX code
            enhanced_latex_code = f'\\dpi{{{dpi_value}}} {size_command} {latex_code}'
            # Encode the LaTeX code for URL
            encoded_latex = urllib.parse.quote(enhanced_latex_code)
            # Use the CodeCogs API to get the image
            url = f"https://latex.codecogs.com/png.latex?{encoded_latex}"
            # Fetch the image
            response = requests.get(url)
            if response.status_code == 200:
                image = QPixmap()
                image.loadFromData(response.content)
                self.latex_image_label.setPixmap(image)
            else:
                self.latex_image_label.setText("Error rendering LaTeX.")
        except Exception as e:
            self.latex_image_label.setText(f"Error rendering LaTeX: {e}")

    def solve_equation(self):
        # Get the current LaTeX code from the text box
        latex_code = self.latex_text.toPlainText().strip()
        if not latex_code:
            self.error_text.setPlainText('No LaTeX code available.')
            self.error_text.show()
            return

        try:
            # Encode the LaTeX code for the URL
            tex = urllib.parse.quote(latex_code)

            # Construct the API URL
            api_url = f"http://api.wolframalpha.com/v2/query?appid={WOLFRAM_APP_ID}&input={tex}&podstate=Step-by-step+solution&format=image&output=json"

            # Make the API request
            res = requests.get(api_url)
            data = res.json()

            # Parse the JSON response
            image_urls = []
            if data['queryresult']['success'] and 'pods' in data['queryresult']:
                pods = data['queryresult']['pods']
                for pod in pods:
                    # Collect images from all pods that have images
                    subpods = pod.get('subpods', [])
                    for subpod in subpods:
                        img = subpod.get('img')
                        if isinstance(img, dict):
                            img_src = img.get('src')
                            if img_src:
                                image_urls.append(img_src)
                        else:
                            print(f"Unexpected img format: {img}")  # For debugging
                self.error_text.clear()
                self.error_text.hide()
            else:
                error_msg = data['queryresult'].get('error', {}).get('msg', 'Wolfram Alpha could not interpret the input.')
                self.clear_solution_images()
                self.error_text.setPlainText(error_msg)
                self.error_text.show()
                return  # Exit the method if the query was not successful

            if image_urls:
                self.display_solution_images(image_urls)
            else:
                self.clear_solution_images()
                self.error_text.setPlainText('No solution images found.')
                self.error_text.show()

        except Exception as e:
            self.clear_solution_images()
            self.error_text.setPlainText(f'An error occurred: {e}')
            self.error_text.show()

    def display_solution_images(self, image_urls):
        # Clear previous images
        self.clear_solution_images()

        for img_url in image_urls:
            try:
                # Download the image
                image_data = urllib.request.urlopen(img_url).read()
                image = QPixmap()
                image.loadFromData(image_data)

                # Get original width and height
                original_width = image.width()
                original_height = image.height()

                # Calculate new width and height
                new_width = original_width * 2
                new_height = original_height * 2

                # Scale the image
                image = image.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                # Create a QLabel to display the image
                image_label = QLabel(self)
                image_label.setAlignment(Qt.AlignCenter)
                image_label.setPixmap(image)

                # Add the image label to the solution layout
                self.solution_layout.addWidget(image_label)
            except Exception as e:
                print(f"Error loading image from {img_url}: {e}")

    def clear_solution_images(self):
        # Remove all widgets from the solution layout
        while self.solution_layout.count():
            child = self.solution_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Set default font size via stylesheet
    app.setStyleSheet("QWidget {font-size: 16pt;}")
    ex = App()
    sys.exit(app.exec_())
