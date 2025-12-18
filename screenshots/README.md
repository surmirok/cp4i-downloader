# Screenshots Directory

This directory contains UI screenshots for the CP4I Downloader web application.

## Required Screenshots

To complete the documentation, please add the following screenshots:

### 1. new-download.png
**What to capture:**
- Navigate to the "New Download" tab
- Show the complete form with all fields visible
- Include component selection dropdown
- Show configuration fields (HOME_DIR, FINAL_REGISTRY, etc.)

**Recommended size:** 1920x1080 or similar

---

### 2. active-downloads.png
**What to capture:**
- Navigate to the "Active Downloads" tab
- Show at least one download in progress
- Display the status, progress, and action buttons
- Include PID information if visible

**Recommended size:** 1920x1080 or similar

---

### 3. history.png
**What to capture:**
- Navigate to the "History" tab
- Show completed and/or failed downloads
- Display action buttons (View Logs, View Report, Retry)
- Include timestamps and status indicators

**Recommended size:** 1920x1080 or similar

---

### 4. view-logs.png
**What to capture:**
- Click "View Logs" button on any download
- Show the log viewer modal with actual log content
- Include the modal header and close button
- Display scrollable log content

**Recommended size:** 1920x1080 or similar

---

### 5. summary-report.png
**What to capture:**
- Click "View Report" button on a completed download
- Show the summary report modal with statistics
- Include download details, timestamps, and status
- Display any error information if applicable

**Recommended size:** 1920x1080 or similar

---

## How to Take Screenshots

### Option 1: Browser Developer Tools
1. Open the web application in your browser
2. Press F12 to open Developer Tools
3. Use the device toolbar to set a consistent viewport size
4. Take screenshots using your OS screenshot tool

### Option 2: Browser Extensions
- **Chrome/Edge:** Use built-in screenshot tool (Ctrl+Shift+P → "Capture screenshot")
- **Firefox:** Right-click → "Take Screenshot"

### Option 3: Command Line Tools
```bash
# Using Firefox headless mode
firefox --headless --screenshot=new-download.png http://localhost:5000

# Using Chrome headless mode
google-chrome --headless --screenshot=new-download.png http://localhost:5000
```

---

## Image Guidelines

- **Format:** PNG (preferred) or JPG
- **Resolution:** Minimum 1280x720, recommended 1920x1080
- **File Size:** Keep under 2MB per image
- **Quality:** Clear, readable text and UI elements
- **Content:** Remove any sensitive information (credentials, internal URLs, etc.)

---

## After Adding Screenshots

Once you've added all screenshots, the README.md will automatically display them in the UI Screenshots section.

The images will be referenced as:
```markdown
![New Download](screenshots/new-download.png)
![Active Downloads](screenshots/active-downloads.png)
![History](screenshots/history.png)
![View Logs](screenshots/view-logs.png)
![Summary Report](screenshots/summary-report.png)
```

---

## Optional: Additional Screenshots

You may also want to add:
- `component-info.png` - Component information display
- `toast-notifications.png` - Success/error toast messages
- `retry-modal.png` - Retry confirmation (if applicable)
- `mobile-view.png` - Responsive mobile layout

---

**Note:** Screenshots help users understand the interface before installation and serve as visual documentation for the project.