# Changelog/ Roadmap

## Features for v3.x

- [ ] Implement database structure
- [ ] Implement unlimited space drawing and annotating
- [ ] Set up testing environment
- [ ] Implement custom settings for shortcuts, annots etc
- [ ] Implement custom colors for annots and drawings
- [ ] Drag&Drop PDF load
- [ ] Custom file opening and saving dialog
- [ ] Implement Page extraction
- [ ] Implement Page moving
- [ ] Implement picture insert
- [ ] Implement pdf drag&drop load
- [ ] Smooth scrolling using QTimeLine
- [ ] Implement bookmarks view panel
- [ ] Add tooltips
- [ ] Implement Forms fill functionality
- [ ] Get more abstraction by splitting up core script
- [ ] Live drawing (currently ui is updated when movement finished)
- [ ] Smoother scrolling
- [ ] Search functionality
- [ ] Custom colors for drawing
- [x] Text Size for Text Boxes
- [ ] Automatic text size from pdf text
- [ ] Change start position of text box line
- [ ] Auto-save in intervalls
- [ ] Focus main window after file handling
- [ ] Store preferred Toolbox position
- [ ] Implement easy toggling of annotation modes
- [ ] Smoother drawing
- [ ] Form estimation (machine vision)
- [x] Implement Goto Page.. functionality

## Features for v2.x

- [x] Creating venv to support fbs
- [x] Button UI Improvement
- [x] Style Optimization
- [x] Implement button pictures
- [x] Abstract PDF annotation properties
- [x] Implement color palettes; workaround, see above
- [x] Implement object moving
- [x] Improve deletion of objects
- [x] Improve moving of objects (lines)
- [x] Implement free drawing
- [x] Improve smoothness on free drawing
- [x] Implement active Pen Support https://doc.qt.io/qt-5/qtabletevent.html
- [ ] Improve text wrapping
- [x] Implement temporary points to indicate ongoing edit
- [x] Improve PDF opening performance
- [x] Save as dialog
- [ ] Implement Undo and Redo functionality
- [ ] Reduce Text Size with increasing annotation length
- [o] Implement object resizing
- [x] Create new PDF
- [ ] Improve text box endpoint position
- [ ] Fix Annotation colors for inverted mode
- [x] PDF overwriting
- [ ] PDF loading indicator
- [o] Implement markdown formatted annotations
- [x] Implement eraser
- [x] Implement Sizes for drawing and marker
- [x] Implement line drawing
- [ ] Implement gestures for touch compatibility
- [x] Improve highlighting by reducing noise on y axis (Kalman?); simply converted to simple rect
- [ ] Threading for pdf loading
- [ ] Threading for pdf saving
- [ ] Threading for pdf rendering
- [x] Implement clear all indicator points
- [x] Implement page insertion
- [x] Improve pdf saving
- [x] Zooming capability via menu

### Issues in 1.x

- [ ] Performance drop when rendering edited pdf file; sometimes reproducable
- [ ] Bug, that a page is displayed twice, after inserting annot; sometimes reproducable
- [ ] Indiator points sometimes not displayed correctly
- [ ] Text not displayed correctly when too much
- [ ] Corporate design for freehand drawings
- [x] much noice while freehand drawing
- [x] In light theme, the button state keeps persistent after deactivation
- [x] Text box can be positioned outside pdf area
- [x] Indicator Points not disappear after cancelling edit
- [ ] Still got issues that pen is suddenly not recogniced anymore. Fixed after restart

## Features for v1.x - Completed

- [x] Cleanup and structure
- [x] Initial PDF rendering
- [x] Inverting PDF colors, dark mode capability
- [x] Implement file loading menu
- [x] Implement scrolling and full PDF load
- [x] Implement zooming
- [x] Improve zooming, by re-rendering page
- [x] Implement mouse paning
- [x] Implement plain-text annotations
- [x] Make loading PDFs faster and safer
- [x] Implement highlighting
- [x] Save PDFs
- [x] Implement plain-text editing
- [x] Improve buttons in toolbox
- [x] Implement delete button -> Cancel text box
- [x] Implement arrow based text boxes
- [o] Comments and code cleaness
- [o] Exception safeness
- [x] In-Field-Test
- [x] Auto-save on exit
- [x] Improve text box positioning
- [o] Introducing fman build system (fbs); suspended due to lack of py 3.7 support

### Issues in 0.x

- [x] PDF loading time
- [x] No 'Delete' option