
# 🖼️ Image Converter GUI (PySide6)

## 🎯 Objective
Create a **Python GUI application using PySide6** that allows users to **drag & drop**, **browse**, or **fetch an image from a URL**, and convert it into different formats:
```

ICO, JPEG, JPG, WebP, PNG

```
The app should also support **image resizing options** with modern GUI design, and allow the user to choose where to save the converted file.

---

## ⚙️ Functional Requirements

### 🧩 1. File Input Options
The application must support **three input methods**:
1. **Drag & Drop** – User can drag any image file into a designated drop area.
2. **File Chooser** – “Browse” button to open file dialog and select image(s).
3. **URL Input** – A text field where user can paste an image URL and fetch it using `requests` or similar library.

Supported input formats (minimum):  
`PNG, JPG, JPEG, BMP, WEBP, GIF, ICO, TIFF, HEIC (if possible)`

---

### 🧩 2. Output Conversion
Users can convert the selected image to **any of the following formats**:
```

ICO, JPEG, JPG, WebP, PNG

```

- Output format is chosen via a **dropdown menu**.
- Use the **Pillow (PIL)** library for format conversion.
- When converted:
  - User can **choose the destination folder** via file dialog.
  - If not chosen, the converted image saves automatically to the user’s **Downloads** folder.

---

### 🧩 3. Image Resizing Options
Include a **dropdown with multiple checkboxes** for resizing options with **unit selection**:

#### Unit Selection
Users can choose between different measurement units:
- **Pixels** - Direct pixel dimensions (default)
- **Centimeters** - Physical size in centimeters (requires DPI setting)
- **Inches** - Physical size in inches (requires DPI setting)

| Size Option | Description |
|--------------|--------------|
| Original | Keep original size |
| 16x16 | Resize to 16×16 (or equivalent in selected unit) |
| 32x32 | Resize to 32×32 (or equivalent in selected unit) |
| 48x48 | Resize to 48×48 (or equivalent in selected unit) |
| 128x128 | Resize to 128×128 (or equivalent in selected unit) |
| 150x150 | Resize to 150×150 (or equivalent in selected unit) |
| 192x192 | Resize to 192×192 (or equivalent in selected unit) |
| 512x512 | Resize to 512×512 (or equivalent in selected unit) |
| Custom x Custom | Allows user to input custom width and height in selected unit |

#### Unit Conversion Examples (at 300 DPI):
- 512 pixels = 4.3 cm = 1.71 inches
- 1.0 cm = 118 pixels
- 1.0 inch = 300 pixels

- If multiple sizes are selected, create multiple converted files (e.g., `image_16x16.png`, `image_512x512.webp`, etc.)
- When using cm/inches, the DPI setting determines the final pixel dimensions

---

### 🧩 4. Modern GUI Features
Use **PySide6** (Qt for Python) for a modern, sleek design:
- **Drag & Drop area** with highlighted border.
- **Progress bar** for image processing.
- **Dropdown menus** for format and size selection.
- **Custom color theme** (light or dark mode toggle optional).
- **Preview area** to display the input image with dimensions and file info.
- **Preview dialog** to show all output images before saving.
- Use layouts (`QVBoxLayout`, `QHBoxLayout`, `QGridLayout`) for clean organization.

#### Preview Features:
- **Main Preview**: Shows loaded image with dimensions, file name, and size
- **Preview Button**: Generate and preview all output images before saving
- **Preview Dialog**: Shows thumbnails of all converted images with:
  - Image preview thumbnails
  - File names and dimensions
  - Format and estimated file sizes
  - Option to cancel or proceed with saving

Suggested GUI sections:
1. Header – Title + Theme toggle (optional)
2. Image Input – Drop area / Browse button / URL field
3. Options – Format dropdown + Resize checkboxes with unit selection
4. Output – Choose save location / default to Downloads
5. Preview + Convert Buttons + Progress Indicator
6. Status / Logs area

---

### 🧩 5. File Saving Behavior
- Converted files should follow the pattern:
```

original_filename_resizedWidthxHeight.format

```
Example:
```

sunset_128x128.webp

```
- Default save location:  
```

C:\Users<username>\Downloads

```
(Use `os.path.expanduser("~")` to locate user's home directory and append `/Downloads`)

---

## 🧠 Technical Requirements

| Component | Description |
|------------|--------------|
| **Language** | Python 3.8+ |
| **Framework** | PySide6 |
| **Image Library** | Pillow (PIL) |
| **Optional Libraries** | `requests` (for URL fetching), `pathlib`, `os`, `io` |
| **GUI Layout** | Modern minimal UI (rounded corners, soft shadow optional) |
| **OS Support** | Windows 10/11, macOS, Linux |

---

## 🧰 Suggested File Structure

```

ImageConverter/
│
├── main.py                    # Entry point
├── ui_mainwindow.py           # PySide6 GUI layout (optional if using Qt Designer)
├── converter.py               # Handles image conversion logic
├── downloader.py              # Handles image fetching from URL
├── utils/
│   ├── file_utils.py          # File path and save location utilities
│   └── resize_options.py      # Resize presets and validation
│
├── assets/
│   ├── icon.png
│   └── style.qss              # Optional stylesheet for modern look
│
└── README.md

````

---

## 🪄 Features for the AI Agent to Implement

1. Create a **main PySide6 window** (`QMainWindow`) with:
   - Drop area (`QLabel` or custom `QWidget` with dragEnterEvent & dropEvent)
   - “Choose File” button
   - “Enter Image URL” field + Fetch button
   - “Output Format” dropdown
   - “Resize Options” dropdown with checkboxes
   - “Save Location” selection button
   - “Convert” button with progress bar
   - “Status” label

2. Implement **drag & drop** support using `event.mimeData().urls()`.
3. Load and preview the dropped/selected/fetched image.
4. Use **Pillow** for conversion:
   ```python![alt text](image.png)
   from PIL import Image
   image = Image.open(file_path)
   image.convert("RGB").save(output_path, format="PNG")
   ````

5. Implement resize logic for multiple selected options.
6. Allow custom width and height input (via dialog box).
7. Automatically save output in selected or default directory.
8. Show conversion progress in a progress bar.
9. Display success/failure messages.

---

## 🧪 Testing Checklist

| Test Case                              | Expected Result                 |
| -------------------------------------- | ------------------------------- |
| Drag a PNG file into app               | Image preview appears           |
| Click “Choose File”                    | Opens file picker               |
| Enter image URL                        | Downloads and previews image    |
| Choose format “ICO” and size “128x128” | Creates resized ICO image       |
| Select multiple sizes                  | Saves multiple converted images |
| No folder selected                     | Saves to Downloads              |
| Invalid file or URL                    | Shows error dialog              |
| Large image                            | Progress bar shows progress     |
| Click "Preview" button                 | Shows preview dialog with thumbnails |
| Preview dialog - Cancel               | Returns to main window without saving |
| Preview dialog - Save All             | Proceeds with conversion        |
| Change units (cm/inches)               | Size labels update accordingly  |

---

## 🧩 Dependencies Installation

```bash
pip install PySide6 Pillow requests
```

---

## 🚀 Run the Application

```bash
python main.py
```

---

## 💡 Optional Enhancements

* Add a **dark/light mode toggle** using `.qss` stylesheets.
* Add **drag-out** feature (drag converted image out of app).
* Allow **batch conversion** for multiple images.
* Remember last used format, size, and folder (save in JSON config).

---

## 📦 Output Example

### Input:

`image.png` (2000×2000)

### Selected Options:

* Format: WebP
* Sizes: 128×128, 512×512

### Output Files:

```
Downloads/
├── image_128x128.webp
└── image_512x512.webp
```

---

## ✅ Success Criteria

* GUI launches with clean, modern layout.
* Supports drag-drop, browse, and URL input.
* Converts between all listed formats.
* Handles multiple resize options correctly.
* Saves files in correct location.
* No crashes or UI freezes during conversion.

---

**Author:** Bibek
**Date:** 30 Oct 2025
**Project Name:** Image Converter GUI
**Language:** Python 3 (PySide6)
**Goal:** A modern, user-friendly image conversion and resizing tool.

