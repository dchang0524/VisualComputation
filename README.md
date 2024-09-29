## VisualComputation
A HackGT Project. \
Converts performs computations on images of equations using Wolfram API and [pix2tex API](https://github.com/lukas-blecher/LaTeX-OCR).

**Required Installations** \
Python3
```sh
pip3 install sympy
pip3 install PyQtWebEngine
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
pip3 install "pix2tex[gui]"
pip3 install PyQt5
pip3 install Pillow
pip3 install requests
pip3 install pyobjc #MacOS Only
```
**Wolfram API Key**
```sh
WOLFRAM_APP_ID = 'YOUR_WOLFRAM_ALPHA_APP_ID'  # Replace with your Wolfram App ID
```
**Run the Application**
```sh
python3 app.py
```
