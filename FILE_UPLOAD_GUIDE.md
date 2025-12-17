# File Upload Feature Guide

## Overview

The CP4I Downloader Web Application now supports uploading custom configuration files instead of using hardcoded values. This allows you to:

- **Upload custom component definitions** (cases.json)
- **Upload custom version mappings** (versions.json)
- **Upload configuration files** (.conf)

## Features

### 1. **Upload Files Button**
Located in the header next to "System Info" and "Configuration" buttons.

### 2. **Three File Types Supported**

#### A. Cases File (cases.json)
Defines the CP4I components available for download.

**Format:**
```json
[
  {
    "name": "ibm-integration-platform-navigator",
    "description": "Platform Navigator",
    "typical_size": "~15GB",
    "versions": ["7.3.2", "7.3.1", "7.3.0"]
  },
  {
    "name": "ibm-apiconnect",
    "description": "API Connect",
    "typical_size": "~25GB",
    "versions": ["10.0.8", "10.0.7"]
  }
]
```

**Fields:**
- `name` (required): Component identifier used by oc ibm-pak
- `description` (required): Human-readable component name
- `typical_size` (optional): Estimated download size
- `versions` (optional): Array of available versions (can be overridden by versions.json)

#### B. Versions File (versions.json)
Maps component names to their available versions. This file overrides the versions defined in cases.json.

**Format:**
```json
{
  "ibm-integration-platform-navigator": [
    "7.3.2",
    "7.3.1",
    "7.3.0",
    "7.2.5"
  ],
  "ibm-apiconnect": [
    "10.0.8",
    "10.0.7",
    "10.0.6"
  ]
}
```

**Usage:**
- Keys must match the `name` field in cases.json
- Values are arrays of version strings
- Versions appear in the dropdown in the order specified

#### C. Configuration File (.conf)
Contains environment variables and settings for the downloader script.

**Format:**
```bash
# CP4I Downloader Configuration
CP4I_ENTITLEMENT_KEY=your_key_here
CP4I_WEBHOOK_URL=https://hooks.slack.com/...
CP4I_NOTIFICATION_EMAIL=admin@example.com
FINAL_REGISTRY=registry.example.com:5000
MAX_PARALLEL_DOWNLOADS=2
MAX_RETRIES=3
MIN_DISK_SPACE_GB=100
VERBOSE=false
```

**Common Variables:**
- `CP4I_ENTITLEMENT_KEY`: IBM entitlement key (required)
- `CP4I_WEBHOOK_URL`: Webhook for notifications (optional)
- `CP4I_NOTIFICATION_EMAIL`: Email for notifications (optional)
- `FINAL_REGISTRY`: Target registry URL
- `MAX_PARALLEL_DOWNLOADS`: Concurrent downloads (default: 2)
- `MAX_RETRIES`: Retry attempts on failure (default: 3)
- `MIN_DISK_SPACE_GB`: Minimum free space required (default: 100)

## How to Use

### Step 1: Prepare Your Files

1. Create your custom JSON files following the formats above
2. Use the provided sample files as templates:
   - `sample-cases.json`
   - `sample-versions.json`
   - `sample-config.conf`

### Step 2: Upload Files

1. Click the **"Upload Files"** button in the header
2. A modal will open with three upload sections
3. For each file type:
   - Click "Choose file" or drag and drop
   - Select your file
   - Click the "Upload" button
4. Wait for the success message

### Step 3: Verify Upload

- **Cases/Versions**: Components will automatically reload with new data
- **Config**: Configuration is saved to `/opt/cp4i/.cp4i-downloader.conf`
- Check the "New Download" tab to see updated components

## File Validation

The application validates uploaded files:

### Cases.json Validation
- ✅ Must be valid JSON
- ✅ Must be an array
- ✅ Each item should have `name` and `description`

### Versions.json Validation
- ✅ Must be valid JSON
- ✅ Must be an object (key-value pairs)
- ✅ Keys should match component names

### Config File Validation
- ✅ Accepts .conf and .txt files
- ✅ No strict validation (bash script will validate)

## File Storage

Uploaded files are stored in:
- **Cases**: `./uploads/cases.json`
- **Versions**: `./uploads/versions.json`
- **Config**: `/opt/cp4i/.cp4i-downloader.conf`

## Fallback Behavior

If no files are uploaded, the application uses **default hardcoded values**:
- 6 common CP4I components
- Recent versions for each component
- Default configuration from script

## Tips

1. **Test with Samples**: Use the provided sample files first
2. **Backup Originals**: Keep copies of your custom files
3. **Incremental Updates**: Upload one file at a time
4. **Verify Changes**: Check the component dropdown after upload
5. **Version Flexibility**: Users can still enter custom versions manually

## Troubleshooting

### Upload Fails
- Check file format (must be valid JSON for cases/versions)
- Ensure file size is under 16MB
- Verify file extension (.json, .conf, .txt)

### Components Not Updating
- Refresh the page
- Check browser console for errors
- Verify JSON structure matches examples

### Config Not Applied
- Ensure file is uploaded successfully
- Check `/opt/cp4i/.cp4i-downloader.conf` exists
- Restart the application if needed

## Security Notes

- Files are validated before saving
- Only JSON and text files accepted
- File size limited to 16MB
- Uploaded files stored in application directory
- Config file may contain sensitive data (entitlement key)

## API Endpoints

For programmatic access:

```bash
# Upload cases file
curl -X POST -F "file=@cases.json" http://localhost:5000/api/upload/cases

# Upload versions file
curl -X POST -F "file=@versions.json" http://localhost:5000/api/upload/versions

# Upload config file
curl -X POST -F "file=@config.conf" http://localhost:5000/api/upload/config

# Get components (includes source: "uploaded" or "default")
curl http://localhost:5000/api/components
```

## Example Workflow

1. **Initial Setup**:
   ```bash
   # Copy sample files
   cp sample-cases.json my-cases.json
   cp sample-versions.json my-versions.json
   cp sample-config.conf my-config.conf
   ```

2. **Customize Files**:
   - Edit `my-cases.json` with your components
   - Edit `my-versions.json` with your versions
   - Edit `my-config.conf` with your settings

3. **Upload via UI**:
   - Open web application
   - Click "Upload Files"
   - Upload each file
   - Verify success messages

4. **Start Download**:
   - Go to "New Download" tab
   - Select component (from your uploaded list)
   - Select version (from your uploaded list)
   - Configure and start download

## Benefits

✅ **Flexibility**: No need to modify code for new components
✅ **Centralized**: Manage all components in one JSON file
✅ **Version Control**: Track changes to component definitions
✅ **Team Sharing**: Share configuration files across team
✅ **Easy Updates**: Update versions without code changes
✅ **Backup/Restore**: Easy to backup and restore configurations

## Support

For issues or questions:
1. Check this guide
2. Review sample files
3. Check application logs
4. Verify JSON syntax with online validators

---

**Made with Bob** 🤖