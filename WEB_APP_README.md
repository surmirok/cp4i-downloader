# CP4I Downloader - Web Application

A modern, user-friendly web interface for managing IBM Cloud Pak for Integration (CP4I) component downloads.

## 🌟 Features

### Web Interface
- ✅ **Modern UI** - Clean, responsive design with IBM Carbon-inspired styling
- ✅ **Real-time Monitoring** - Live updates of download progress
- ✅ **Component Library** - Pre-configured list of common CP4I components
- ✅ **Download Management** - Start, stop, retry, and monitor downloads
- ✅ **Configuration Editor** - Web-based configuration management
- ✅ **System Information** - View prerequisites and disk space
- ✅ **Log Viewer** - View download logs and reports in the browser
- ✅ **Download History** - Track all past downloads

### Backend API
- ✅ **RESTful API** - Clean API endpoints for all operations
- ✅ **Process Management** - Background download process handling
- ✅ **Status Tracking** - Real-time download status updates
- ✅ **Auto-refresh** - Automatic updates every 10 seconds

## 📋 Prerequisites

### System Requirements
- Python 3.8 or higher
- All prerequisites from the main script (oc, podman, curl, jq, etc.)
- Web browser (Chrome, Firefox, Safari, Edge)

### Python Dependencies
- Flask 3.0.0
- Flask-CORS 4.0.0
- python-dotenv 1.0.0

## 🚀 Installation

### 1. Install Python Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using pip3
pip3 install -r requirements.txt

# Using virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Verify Script Permissions

```bash
chmod +x cp4i_downloader.sh
```

### 3. Ensure Directory Structure

```
CP4I/
├── app.py                      # Flask backend
├── cp4i_downloader.sh          # Main download script
├── requirements.txt            # Python dependencies
├── templates/
│   └── index.html             # Web interface
├── static/
│   ├── css/
│   │   └── style.css          # Styles
│   └── js/
│       └── app.js             # Frontend JavaScript
└── README.md                   # Documentation
```

## 🎯 Usage

### Starting the Web Application

#### Development Mode

```bash
# Start the Flask development server
python3 app.py

# Or with explicit host and port
python3 app.py --host 0.0.0.0 --port 5000
```

The application will be available at:
- Local: http://localhost:5000
- Network: http://YOUR_IP:5000

#### Production Mode

For production deployment, use a WSGI server like Gunicorn:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With more workers and timeout
gunicorn -w 8 -b 0.0.0.0:5000 --timeout 300 app:app
```

### Using the Web Interface

#### 1. Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

#### 2. Start a New Download

1. Click on the **"New Download"** tab
2. Select a component from the dropdown
3. Choose a version
4. Enter a directory name (auto-filled based on component)
5. (Optional) Add a filter pattern
6. (Optional) Check "Dry Run" to preview without downloading
7. Click **"Start Download"**

#### 3. Monitor Active Downloads

1. Click on the **"Active Downloads"** tab
2. View real-time status of running downloads
3. Click **"Details"** to see logs and progress
4. Click **"Stop"** to terminate a running download

#### 4. View Download History

1. Click on the **"History"** tab
2. View completed, failed, or stopped downloads
3. Click **"View Logs"** to see download logs
4. Click **"View Report"** to see summary reports

#### 5. Configure Settings

1. Click **"Configuration"** in the header
2. Edit the configuration file
3. Click **"Save Configuration"**

Configuration example:
```bash
# IBM Entitlement Key
CP4I_ENTITLEMENT_KEY="your_entitlement_key_here"

# Notification Settings
CP4I_WEBHOOK_URL="https://your-webhook-url.com/notify"
CP4I_NOTIFICATION_EMAIL="admin@example.com"

# Performance Settings
MAX_PARALLEL_DOWNLOADS=2
MIN_DISK_SPACE_GB=100
MAX_RETRIES=3
RETRY_BASE_DELAY=5
```

#### 6. Check System Information

1. Click **"System Info"** in the header
2. View disk space, prerequisites, and system configuration

## 📡 API Endpoints

### System Information

```bash
# Get system info
GET /api/system/info

# Response
{
  "disk_info": "...",
  "prerequisites": {
    "oc": true,
    "podman": true,
    "curl": true,
    "jq": true,
    "oc-ibm-pak": true
  },
  "home_dir": "/opt/cp4i",
  "script_path": "/path/to/cp4i_downloader.sh"
}
```

### Configuration

```bash
# Get configuration
GET /api/config

# Update configuration
POST /api/config
Content-Type: application/json
{
  "config": "CP4I_ENTITLEMENT_KEY=your_key\n..."
}
```

### Downloads

```bash
# List all downloads
GET /api/downloads

# Start new download
POST /api/downloads
Content-Type: application/json
{
  "component": "ibm-integration-platform-navigator",
  "version": "7.3.2",
  "name": "pn-7.3.2",
  "filter": ".*management.*",  // optional
  "dry_run": false              // optional
}

# Get download details
GET /api/downloads/{download_id}

# Stop download
DELETE /api/downloads/{download_id}

# Retry download
POST /api/downloads/{download_id}/retry
```

### Logs and Reports

```bash
# Get download logs
GET /api/logs/{name}

# Get summary report
GET /api/reports/{name}
```

### Components

```bash
# Get list of components
GET /api/components

# Response
{
  "components": [
    {
      "name": "ibm-integration-platform-navigator",
      "description": "Platform Navigator",
      "typical_size": "~15GB",
      "versions": ["7.3.2", "7.3.1", "7.3.0"]
    },
    ...
  ]
}
```

### Validation

```bash
# Validate prerequisites
POST /api/validate
```

## 🎨 UI Features

### Dashboard
- **Component Selection**: Dropdown with descriptions and sizes
- **Auto-fill**: Automatic directory name generation
- **Component Info**: Display component details when selected
- **Form Validation**: Client-side validation before submission

### Active Downloads
- **Status Badges**: Color-coded status indicators
- **Progress Bars**: Visual progress indication
- **Action Buttons**: Stop, retry, view details
- **Auto-refresh**: Updates every 10 seconds

### Download Details Modal
- **Full Information**: Component, version, status, timestamps
- **Log Tail**: Recent log output
- **Progress Summary**: Download statistics

### System Info Modal
- **Disk Space**: Available storage information
- **Prerequisites**: Installation status of required tools
- **Configuration**: System paths and settings

### Configuration Editor
- **Syntax Highlighting**: Monospace font for config editing
- **Save/Reload**: Easy configuration management
- **Validation**: Server-side validation

## 🔧 Customization

### Changing the Port

Edit `app.py`:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)  # Change port here
```

### Changing the Home Directory

Edit `app.py`:
```python
HOME_DIR = "/your/custom/path"
```

### Adding Custom Components

Edit the `get_components()` function in `app.py`:
```python
components = [
    {
        "name": "your-custom-component",
        "description": "Custom Component",
        "typical_size": "~10GB",
        "versions": ["1.0.0", "1.0.1"]
    },
    ...
]
```

### Customizing Styles

Edit `static/css/style.css` to change colors, fonts, or layout:
```css
:root {
    --primary-color: #your-color;
    --secondary-color: #your-color;
    ...
}
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or use a different port
python3 app.py --port 8080
```

### Permission Denied

```bash
# Ensure script is executable
chmod +x cp4i_downloader.sh

# Check directory permissions
ls -la /opt/cp4i
```

### Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Cannot Connect to API

1. Check if Flask is running: `ps aux | grep python`
2. Check firewall settings: `sudo firewall-cmd --list-all`
3. Verify the port is open: `netstat -tuln | grep 5000`

### Downloads Not Starting

1. Verify script path in `app.py`
2. Check script permissions: `ls -la cp4i_downloader.sh`
3. Verify prerequisites: Click "System Info" in the UI
4. Check logs: `tail -f /opt/cp4i/*/download.log`

## 🔒 Security Considerations

### Production Deployment

1. **Use HTTPS**: Configure SSL/TLS certificates
2. **Authentication**: Add user authentication (Flask-Login, OAuth)
3. **Rate Limiting**: Implement rate limiting (Flask-Limiter)
4. **Input Validation**: Already implemented, but review for your use case
5. **CORS**: Configure CORS properly for your domain
6. **Environment Variables**: Use `.env` file for sensitive data

### Example with Authentication

```python
from flask_login import LoginManager, login_required

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
@login_required
def index():
    return render_template('index.html')
```

### Example with HTTPS

```bash
# Generate self-signed certificate (development only)
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Run with SSL
python3 app.py --cert cert.pem --key key.pem
```

## 📊 Monitoring

### Application Logs

```bash
# View Flask logs
tail -f /var/log/cp4i-web/app.log

# View download logs
tail -f /opt/cp4i/*/download.log
```

### System Monitoring

```bash
# Monitor CPU and memory
top -p $(pgrep -f app.py)

# Monitor disk space
watch -n 5 df -h /opt/cp4i

# Monitor network
netstat -tuln | grep 5000
```

## 🚀 Advanced Features

### Running as a Service

Create a systemd service file `/etc/systemd/system/cp4i-web.service`:

```ini
[Unit]
Description=CP4I Downloader Web Application
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/CP4I
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 /path/to/CP4I/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cp4i-web
sudo systemctl start cp4i-web
sudo systemctl status cp4i-web
```

### Nginx Reverse Proxy

Configure Nginx as a reverse proxy:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t cp4i-downloader-web .
docker run -d -p 5000:5000 -v /opt/cp4i:/opt/cp4i cp4i-downloader-web
```

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [IBM Cloud Pak for Integration](https://www.ibm.com/docs/en/cloud-paks/cp-integration)
- [OpenShift CLI Documentation](https://docs.openshift.com/container-platform/latest/cli_reference/openshift_cli/getting-started-cli.html)

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows Python PEP 8 style guide
- JavaScript follows ES6+ standards
- UI changes are responsive and accessible
- API changes are documented
- Testing is performed before submission

## 📄 License

This web application is provided as-is for use with IBM Cloud Pak for Integration. Refer to IBM's licensing terms for the actual software components.

---

**Web Application Version**: 2.0.0  
**Last Updated**: December 2025  
**Maintained by**: DevOps Team