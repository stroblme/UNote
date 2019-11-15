# UNote

**Latest release: v1.3**

Fills the lack of an open-source PDF Editor with the capability to draw and add notes not only to the PDF pages but to a virtually unlimited space.

## Features

- PDF Annotating
    - Text Boxes (with and without pointers)
    - Highlighting
    - Freehand drawing
    - Erasing
- PDF Tools
    - Insert/ Delete Pages
    - Rearrange Pages
    - Create PDFs
- Additional Features
    - Active Pen Support
    - Automatic Form Detection From Freehand Annotations
    - Various Options For Annotation Tools
    - Dark/ Light Mode
    - Fast PDF Loading


See [CHANGELOG.md](https://gitlab.com/stroblme/unote/blob/master/CHANGELOG.md) for a complete list of latest features in the current release

Installer files will be updated once, a major version (vX.0) is achieved.

## Shortcuts

- Ctrl-T: Add Text Box
- Ctrl-D: Freehand Draw
- Ctrl-M: Mark/ Highlight Mode
- Ctrl-E: Eraser
- Ctrl-S: Save
- Ctrl-P: Open Preferences
- Ctrl-Q: Save and Quit application
- Esc: Cancel
- Ctrl-Return: Confirm

## Requirements

- Python3.6
- PyQt5
- Pillow
- PyMuPDF
- fbs
- indexed.py
- numpy
- scipy

In the environment, simply run:
```
pip install -r requirements.txt
```



## Building

Uses fbs:
https://github.com/mherrmann/fbs-tutorial