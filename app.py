#!/usr/bin/env python3
"""
CP4I Downloader Web Application
Flask-based web interface for managing CP4I component downloads
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import os
import json
import threading
import time
from datetime import datetime
import glob

app = Flask(__name__)
CORS(app)

# Configuration
HOME_DIR = "/opt/cp4i"
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "cp4i_downloader.sh")
CONFIG_FILE = os.path.join(HOME_DIR, ".cp4i-downloader.conf")

# In-memory storage for active downloads
active_downloads = {}
download_history = []

class DownloadManager:
    """Manages download processes and their status"""
    
    def __init__(self):
        self.downloads = {}
        self.lock = threading.Lock()
    
    def _generate_summary_report(self, download):
        """Generate a comprehensive summary report for a download"""
        try:
            home_dir = download.get('home_dir', HOME_DIR)
            name = download.get('name')
            component = download.get('component')
            version = download.get('version')
            status = download.get('status')
            start_time = download.get('start_time')
            end_time = download.get('end_time')
            final_registry = download.get('final_registry', 'N/A')
            registry_auth_file = download.get('registry_auth_file', 'N/A')
            filter_pattern = download.get('filter', 'None')
            pid = download.get('pid', 'N/A')
            return_code = download.get('return_code', 'N/A')
            
            # Calculate duration
            try:
                start_dt = datetime.fromisoformat(start_time)
                end_dt = datetime.fromisoformat(end_time)
                duration = str(end_dt - start_dt)
                duration_seconds = (end_dt - start_dt).total_seconds()
            except:
                duration = "N/A"
                duration_seconds = 0
            
            # Get directory information
            download_dir = f"{home_dir}/{name}"
            dir_size = "N/A"
            dir_size_bytes = 0
            if os.path.exists(download_dir):
                try:
                    result = subprocess.run(
                        f"du -sh {download_dir}",
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        dir_size = result.stdout.split()[0]
                    
                    # Get size in bytes
                    result_bytes = subprocess.run(
                        f"du -sb {download_dir}",
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    if result_bytes.returncode == 0:
                        dir_size_bytes = int(result_bytes.stdout.split()[0])
                except:
                    pass
            
            # Count files and directories
            file_count = 0
            dir_count = 0
            image_files = 0
            mapping_files = 0
            log_files = 0
            if os.path.exists(download_dir):
                try:
                    for root, dirs, files in os.walk(download_dir):
                        dir_count += len(dirs)
                        file_count += len(files)
                        for f in files:
                            if f.endswith(('.tar', '.tar.gz', '.tgz')):
                                image_files += 1
                            elif 'mapping' in f.lower():
                                mapping_files += 1
                            elif f.endswith('.log'):
                                log_files += 1
                except:
                    pass
            
            # Check for specific files
            log_file = f"{download_dir}/{name}-download.log"
            mapping_file = f"{download_dir}/mapping.txt"
            config_file = f"{download_dir}/.image-config.json"
            
            log_exists = "Yes" if os.path.exists(log_file) else "No"
            mapping_exists = "Yes" if os.path.exists(mapping_file) else "No"
            config_exists = "Yes" if os.path.exists(config_file) else "No"
            
            # Get log file size
            log_size = "N/A"
            if os.path.exists(log_file):
                try:
                    log_size_bytes = os.path.getsize(log_file)
                    if log_size_bytes < 1024:
                        log_size = f"{log_size_bytes} B"
                    elif log_size_bytes < 1024*1024:
                        log_size = f"{log_size_bytes/1024:.2f} KB"
                    else:
                        log_size = f"{log_size_bytes/(1024*1024):.2f} MB"
                except:
                    pass
            
            # Count images in mapping file
            image_count_from_mapping = 0
            if os.path.exists(mapping_file):
                try:
                    with open(mapping_file, 'r') as f:
                        image_count_from_mapping = len([line for line in f if line.strip() and not line.startswith('#')])
                except:
                    pass
            
            # Get system information
            hostname = "N/A"
            try:
                result = subprocess.run("hostname", shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    hostname = result.stdout.strip()
            except:
                pass
            
            # Get disk space
            disk_space = "N/A"
            try:
                result = subprocess.run(
                    f"df -h {home_dir} | tail -1",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    parts = result.stdout.split()
                    if len(parts) >= 5:
                        disk_space = f"Total: {parts[1]}, Used: {parts[2]}, Available: {parts[3]}, Use%: {parts[4]}"
            except:
                pass
            
            # Calculate transfer rate
            transfer_rate = "N/A"
            if dir_size_bytes > 0 and duration_seconds > 0:
                rate_mbps = (dir_size_bytes / (1024*1024)) / duration_seconds
                transfer_rate = f"{rate_mbps:.2f} MB/s"
            
            # Get error information from log if failed
            error_info = ""
            if status == "failed" and os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        # Get last 10 lines for error context
                        error_lines = [line.strip() for line in lines[-10:] if 'error' in line.lower() or 'fail' in line.lower()]
                        if error_lines:
                            error_info = "\n".join(error_lines[:5])  # Show up to 5 error lines
                except:
                    pass
            
            # Generate report content
            report_content = f"""
================================================================================
                    CP4I DOWNLOAD SUMMARY REPORT
================================================================================

DOWNLOAD INFORMATION
--------------------
Component:              {component}
Version:                {version}
Directory Name:         {name}
Status:                 {status.upper()}
Process ID:             {pid}
Exit Code:              {return_code}

TIMING DETAILS
--------------
Start Time:             {start_time}
End Time:               {end_time}
Duration:               {duration}
Transfer Rate:          {transfer_rate}

CONFIGURATION
-------------
Home Directory:         {home_dir}
Download Directory:     {download_dir}
Target Registry:        {final_registry}
Registry Auth File:     {registry_auth_file}
Filter Pattern:         {filter_pattern}

FILE SYSTEM DETAILS
-------------------
Directory Exists:       {'Yes' if os.path.exists(download_dir) else 'No'}
Directory Size:         {dir_size}
Total Files:            {file_count}
Total Directories:      {dir_count}
Image Files (.tar):     {image_files}
Mapping Files:          {mapping_files}
Log Files:              {log_files}

KEY FILES
---------
Download Log:           {log_file}
  - Exists:             {log_exists}
  - Size:               {log_size}

Mapping File:           {mapping_file}
  - Exists:             {mapping_exists}
  - Images Listed:      {image_count_from_mapping}

Config File:            {config_file}
  - Exists:             {config_exists}

SYSTEM INFORMATION
------------------
Hostname:               {hostname}
Disk Space ({home_dir}):
  {disk_space}
"""
            
            # Add error information if failed
            if error_info:
                report_content += f"""
ERROR DETAILS
-------------
Recent errors from log file:
{error_info}
"""
            
            report_content += f"""
================================================================================
Report Generated:       {datetime.now().isoformat()}
================================================================================
"""
            
            # Save report to file
            report_file = f"{home_dir}/{name}-summary-report.txt"
            os.makedirs(home_dir, exist_ok=True)
            with open(report_file, 'w') as f:
                f.write(report_content)
            
            print(f"[REPORT] Comprehensive summary report generated: {report_file}")
            return report_file
            
        except Exception as e:
            print(f"[REPORT] Error generating summary report: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def start_download(self, download_id, component, version, name, filter_pattern=None, dry_run=False,
                      home_dir=None, final_registry=None, registry_auth_file=None, entitlement_key=None):
        """Start a new download process"""
        with self.lock:
            if download_id in self.downloads:
                return {"error": "Download already in progress"}
            
            # Use provided values or defaults
            home_dir = home_dir or HOME_DIR
            final_registry = final_registry or "registry.example.com:5000"
            registry_auth_file = registry_auth_file or "/root/.docker/config.json"
            
            # Build command
            cmd = [
                "bash", SCRIPT_PATH,
                "--component", component,
                "--version", version,
                "--name", name
            ]
            
            if filter_pattern:
                cmd.extend(["--filter", filter_pattern])
            
            if dry_run:
                cmd.append("--dry-run")
            
            # Build environment variables
            env = os.environ.copy()
            env["HOME_DIR"] = home_dir
            env["FINAL_REGISTRY"] = final_registry
            env["REGISTRY_AUTH_FILE"] = registry_auth_file
            if entitlement_key:
                env["ENTITLEMENT_KEY"] = entitlement_key
            
            # Start process
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env
                )
                
                self.downloads[download_id] = {
                    "id": download_id,
                    "component": component,
                    "version": version,
                    "name": name,
                    "filter": filter_pattern,
                    "process": process,
                    "status": "running",
                    "start_time": datetime.now().isoformat(),
                    "pid": process.pid,
                    "mirror_pid": None,  # Will be populated by monitoring
                    "log_file": f"{home_dir}/{name}/{name}-download.log",
                    "home_dir": home_dir,
                    "final_registry": final_registry
                }
                
                # Start monitoring thread
                threading.Thread(
                    target=self._monitor_download,
                    args=(download_id,),
                    daemon=True
                ).start()
                
                return {"success": True, "download_id": download_id, "pid": process.pid}
            
            except Exception as e:
                return {"error": str(e)}
    
    def _monitor_download(self, download_id):
        """Monitor download process and check log for completion"""
        download = self.downloads.get(download_id)
        if not download:
            return
        
        process = download["process"]
        log_file = download.get("log_file")
        last_log_size = 0
        last_activity_time = time.time()
        check_interval = 30  # Check every 30 seconds
        
        print(f"Starting monitoring for {download_id}, log file: {log_file}")
        
        # Monitor process and log file
        while True:
            # Check if process has finished
            if process.poll() is not None:
                print(f"[{download_id}] Process finished with code {process.returncode}")
                break
            # Check log file for completion message and mirror PID
            if log_file and os.path.exists(log_file):
                try:
                    # Get current file size
                    current_size = os.path.getsize(log_file)
                    
                    # Read log content
                    with open(log_file, 'r') as f:
                        log_content = f.read()
                        lines = log_content.strip().split('\n')
                        last_line = lines[-1] if lines else ""
                        
                        print(f"[{download_id}] Last line: {last_line[:100]}")
                        
                        # Extract mirror PID if not already captured
                        if not download.get("mirror_pid"):
                            import re
                            pid_match = re.search(r'Image mirroring started.*\(PID:\s*(\d+)\)', log_content)
                            if pid_match:
                                with self.lock:
                                    download["mirror_pid"] = int(pid_match.group(1))
                                    print(f"Captured mirror PID: {download['mirror_pid']} for {download_id}")
                        
                        # Check if log is growing (new activity)
                        if current_size > last_log_size:
                            last_activity_time = time.time()
                            last_log_size = current_size
                            with self.lock:
                                if download["status"] != "completed":
                                    download["status"] = "progressing"
                                    # Calculate rough progress based on log activity
                                    download["progress"] = min(95, download.get("progress", 0) + 5)
                            print(f"[{download_id}] Log growing, status: progressing")
                        
                        # Check for error in last line
                        if "error: one or more errors occurred" in last_line.lower():
                            print(f"[{download_id}] ERROR DETECTED in last line!")
                            with self.lock:
                                if download["status"] != "failed":
                                    download["status"] = "failed"
                                    download["end_time"] = datetime.now().isoformat()
                                    print(f"Download {download_id} marked as failed")
                                    
                                    # Generate summary report for failed download
                                    self._generate_summary_report(download)
                                    
                                    # Add to history immediately
                                    download_history.append({
                                        "id": download_id,
                                        "component": download["component"],
                                        "version": download["version"],
                                        "name": download["name"],
                                        "filter": download.get("filter"),
                                        "status": "failed",
                                        "start_time": download["start_time"],
                                        "end_time": download["end_time"],
                                        "home_dir": download.get("home_dir"),
                                        "final_registry": download.get("final_registry"),
                                        "registry_auth_file": download.get("registry_auth_file"),
                                        "entitlement_key": download.get("entitlement_key")
                                    })
                                    print(f"Added {download_id} to history as failed")
                            
                            # Wait then remove from active downloads
                            print(f"[{download_id}] Waiting 5 seconds before removal...")
                            time.sleep(5)
                            with self.lock:
                                if download_id in self.downloads:
                                    del self.downloads[download_id]
                                    print(f"[{download_id}] Removed from active downloads")
                            
                            # Exit monitoring loop
                            return
                        
                        # Check for completion in last line
                        if "info: mirroring completed" in last_line.lower():
                            print(f"[{download_id}] COMPLETION DETECTED in last line!")
                            with self.lock:
                                if download["status"] != "completed":
                                    download["status"] = "completed"
                                    download["progress"] = 100
                                    download["end_time"] = datetime.now().isoformat()
                                    print(f"Download {download_id} marked as completed")
                                    
                                    # Generate summary report for completed download
                                    self._generate_summary_report(download)
                                    
                                    # Add to history immediately
                                    download_history.append({
                                        "id": download_id,
                                        "component": download["component"],
                                        "version": download["version"],
                                        "name": download["name"],
                                        "filter": download.get("filter"),
                                        "status": "completed",
                                        "start_time": download["start_time"],
                                        "end_time": download["end_time"],
                                        "home_dir": download.get("home_dir"),
                                        "final_registry": download.get("final_registry"),
                                        "registry_auth_file": download.get("registry_auth_file"),
                                        "entitlement_key": download.get("entitlement_key")
                                    })
                                    print(f"Added {download_id} to history")
                            
                            # Wait then remove from active downloads
                            print(f"[{download_id}] Waiting 5 seconds before removal...")
                            time.sleep(5)
                            with self.lock:
                                if download_id in self.downloads:
                                    del self.downloads[download_id]
                                    print(f"[{download_id}] Removed from active downloads")
                            
                            # Exit monitoring loop
                            return
                        
                except Exception as e:
                    print(f"Error monitoring {download_id}: {e}")
            
            time.sleep(check_interval)  # Check every 30 seconds
        
        # Process finished - check one last time for completion
        print(f"[{download_id}] Process loop ended, return code: {process.returncode}")
        
        # Check if it was a successful dry-run, actual completion, or error
        if log_file and os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    log_content = f.read()
                    lines = log_content.strip().split('\n')
                    last_line = lines[-1] if lines else ""
                    
                    # Check for error in last line first
                    if "error: one or more errors occurred" in last_line.lower():
                        print(f"[{download_id}] Final check: ERROR DETECTED in last line!")
                        
                        with self.lock:
                            if download_id in self.downloads and download["status"] != "failed":
                                download["status"] = "failed"
                                download["end_time"] = datetime.now().isoformat()
                                
                                # Generate summary report
                                self._generate_summary_report(download)
                                
                                # Add to history with configuration
                                download_history.append({
                                    "id": download_id,
                                    "component": download["component"],
                                    "version": download["version"],
                                    "name": download["name"],
                                    "filter": download.get("filter"),
                                    "status": "failed",
                                    "start_time": download["start_time"],
                                    "end_time": download["end_time"],
                                    "home_dir": download.get("home_dir"),
                                    "final_registry": download.get("final_registry"),
                                    "registry_auth_file": download.get("registry_auth_file"),
                                    "entitlement_key": download.get("entitlement_key")
                                })
                                print(f"[{download_id}] Added to history as failed")
                        
                        # Wait then remove
                        time.sleep(5)
                        with self.lock:
                            if download_id in self.downloads:
                                del self.downloads[download_id]
                                print(f"[{download_id}] Removed from active downloads")
                        return
                    
                    # Check for completion message OR successful dry-run
                    is_completed = "info: mirroring completed" in last_line.lower()
                    is_dry_run = "[dry run]" in log_content.lower() and process.returncode == 0
                    
                    if is_completed or is_dry_run:
                        status_msg = "DRY RUN completed" if is_dry_run else "COMPLETION DETECTED"
                        print(f"[{download_id}] Final check: {status_msg}!")
                        
                        with self.lock:
                            if download_id in self.downloads and download["status"] != "completed":
                                download["status"] = "completed"
                                download["progress"] = 100
                                download["end_time"] = datetime.now().isoformat()
                                
                                # Generate summary report
                                self._generate_summary_report(download)
                                
                                # Add to history with configuration
                                download_history.append({
                                    "id": download_id,
                                    "component": download["component"],
                                    "version": download["version"],
                                    "name": download["name"],
                                    "filter": download.get("filter"),
                                    "status": "completed",
                                    "start_time": download["start_time"],
                                    "end_time": download["end_time"],
                                    "home_dir": download.get("home_dir"),
                                    "final_registry": download.get("final_registry"),
                                    "registry_auth_file": download.get("registry_auth_file"),
                                    "entitlement_key": download.get("entitlement_key")
                                })
                                print(f"[{download_id}] Added to history as completed")
                        
                        # Wait then remove
                        time.sleep(5)
                        with self.lock:
                            if download_id in self.downloads:
                                del self.downloads[download_id]
                                print(f"[{download_id}] Removed from active downloads")
                        return
            except Exception as e:
                print(f"Error in final check for {download_id}: {e}")
        
        # If not completed and exit code is non-zero, mark as failed
        if process.returncode != 0:
            print(f"[{download_id}] Process ended with error code {process.returncode}")
            with self.lock:
                if download_id in self.downloads:
                    download["status"] = "failed"
                    download["end_time"] = datetime.now().isoformat()
                    
                    # Generate summary report for failed download
                    self._generate_summary_report(download)
                    
                    download_history.append({
                        "id": download_id,
                        "component": download["component"],
                        "version": download["version"],
                        "name": download["name"],
                        "filter": download.get("filter"),
                        "status": "failed",
                        "start_time": download["start_time"],
                        "end_time": download["end_time"],
                        "home_dir": download.get("home_dir"),
                        "final_registry": download.get("final_registry"),
                        "registry_auth_file": download.get("registry_auth_file"),
                        "entitlement_key": download.get("entitlement_key")
                    })
                    del self.downloads[download_id]
                    print(f"[{download_id}] Marked as failed and moved to history")
        else:
            # Exit code 0 but no completion message - treat as completed
            print(f"[{download_id}] Process ended successfully (exit code 0)")
            with self.lock:
                if download_id in self.downloads:
                    download["status"] = "completed"
                    download["progress"] = 100
                    download["end_time"] = datetime.now().isoformat()
                    
                    # Generate summary report
                    self._generate_summary_report(download)
                    download_history.append({
                        "id": download_id,
                        "component": download["component"],
                        "version": download["version"],
                        "name": download["name"],
                        "filter": download.get("filter"),
                        "status": "completed",
                        "start_time": download["start_time"],
                        "end_time": download["end_time"],
                        "home_dir": download.get("home_dir"),
                        "final_registry": download.get("final_registry"),
                        "registry_auth_file": download.get("registry_auth_file"),
                        "entitlement_key": download.get("entitlement_key")
                    })
                    del self.downloads[download_id]
                    print(f"[{download_id}] Marked as completed and moved to history")
        
        # Process finished - already added to history above in lines 260-273 or 284-297
        # No need to add again here
    
    def dismiss_download(self, download_id):
        """Remove a download from active list and kill background process"""
        with self.lock:
            if download_id in self.downloads:
                download = self.downloads[download_id]
                
                # Kill the mirror process (nohup oc image mirror)
                mirror_pid = download.get("mirror_pid")
                main_pid = download.get("pid")
                name = download.get("name")
                
                killed_pids = []
                
                # Try to kill mirror PID first (this is the actual download process)
                if mirror_pid:
                    try:
                        os.kill(mirror_pid, 9)
                        killed_pids.append(f"mirror:{mirror_pid}")
                        print(f"Killed mirror process {mirror_pid} for download {download_id}")
                    except ProcessLookupError:
                        print(f"Mirror process {mirror_pid} already terminated")
                    except Exception as e:
                        print(f"Error killing mirror process {mirror_pid}: {e}")
                
                # Kill main script process and all children
                if main_pid:
                    try:
                        # Kill all child processes first
                        subprocess.run(
                            f"pkill -9 -P {main_pid}",
                            shell=True,
                            capture_output=True
                        )
                        # Then kill main process
                        os.kill(main_pid, 9)
                        killed_pids.append(f"main:{main_pid}")
                        print(f"Killed main process {main_pid} and children for download {download_id}")
                    except ProcessLookupError:
                        print(f"Main process {main_pid} already terminated")
                    except Exception as e:
                        print(f"Error killing main process {main_pid}: {e}")
                
                # Also try to kill any remaining oc image mirror processes for this download
                try:
                    result = subprocess.run(
                        f"pkill -9 -f 'oc image mirror.*{name}'",
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print(f"Killed additional oc image mirror processes for {name}")
                except Exception as e:
                    print(f"Error killing additional processes: {e}")
                
                # Mark as dismissed and add to history
                download["status"] = "dismissed"
                download["end_time"] = datetime.now().isoformat()
                
                # Generate summary report for dismissed download
                self._generate_summary_report(download)
                
                # Add to history with configuration so logs/reports can be accessed
                download_history.append({
                    "id": download_id,
                    "component": download["component"],
                    "version": download["version"],
                    "name": download["name"],
                    "filter": download.get("filter"),
                    "status": "dismissed",
                    "start_time": download["start_time"],
                    "end_time": download["end_time"],
                    "home_dir": download.get("home_dir"),
                    "final_registry": download.get("final_registry"),
                    "registry_auth_file": download.get("registry_auth_file"),
                    "entitlement_key": download.get("entitlement_key")
                })
                
                # Remove from active downloads
                del self.downloads[download_id]
                
                pids_msg = f"PIDs killed: {killed_pids}" if killed_pids else "No active processes found"
                return {"success": True, "message": f"Download dismissed. {pids_msg}"}
            return {"error": "Download not found"}
    
    def get_download_status(self, download_id):
        """Get status of a specific download"""
        with self.lock:
            download = self.downloads.get(download_id)
            if not download:
                return {"error": "Download not found"}
            
            # Get log tail
            log_tail = self._get_log_tail(download.get("log_file"))
            
            # Get progress if available
            progress = self._get_progress(download.get("name"))
            
            return {
                "id": download_id,
                "component": download["component"],
                "version": download["version"],
                "name": download["name"],
                "status": download["status"],
                "start_time": download["start_time"],
                "end_time": download.get("end_time"),
                "pid": download.get("pid"),
                "log_tail": log_tail,
                "progress": progress
            }
    
    def get_all_downloads(self):
        """Get status of all downloads"""
        with self.lock:
            # Return serializable data only (exclude process object)
            return [{
                "id": d["id"],
                "component": d["component"],
                "version": d["version"],
                "name": d["name"],
                "filter": d.get("filter"),
                "status": d["status"],
                "start_time": d["start_time"],
                "end_time": d.get("end_time"),
                "pid": d.get("mirror_pid") or d.get("pid"),  # Show mirror PID if available
                "main_pid": d.get("pid"),
                "mirror_pid": d.get("mirror_pid"),
                "return_code": d.get("return_code"),
                "progress": d.get("progress", 0)
            } for d in self.downloads.values()]
    
    def stop_download(self, download_id):
        """Stop a running download"""
        with self.lock:
            download = self.downloads.get(download_id)
            if not download:
                return {"error": "Download not found"}
            
            if download["status"] != "running":
                return {"error": "Download is not running"}
            
            try:
                download["process"].terminate()
                download["status"] = "stopped"
                download["end_time"] = datetime.now().isoformat()
                return {"success": True}
            except Exception as e:
                return {"error": str(e)}
    
    def _get_log_tail(self, log_file, lines=50):
        """Get last N lines from log file"""
        if not log_file or not os.path.exists(log_file):
            return []
        
        try:
            with open(log_file, 'r') as f:
                return f.readlines()[-lines:]
        except:
            return []
    
    def _get_progress(self, download_id):
        """Get download progress"""
        download = self.downloads.get(download_id)
        if not download:
            return None
        
        name = download.get('name')
        home_dir = download.get('home_dir', HOME_DIR)
        
        if not name:
            return None
        
        summary_file = f"{home_dir}/{name}/{name}-summary-report.txt"
        if os.path.exists(summary_file):
            try:
                with open(summary_file, 'r') as f:
                    content = f.read()
                    # Parse summary for progress info
                    return {"summary": content}
            except:
                pass
        
        return None

# Initialize download manager
download_manager = DownloadManager()

# Routes
@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/system/info', methods=['GET'])
def system_info():
    """Get system information"""
    try:
        # Get home_dir from query parameter or use default
        home_dir = request.args.get('home_dir', HOME_DIR)
        
        # Check disk space
        disk_info = subprocess.run(
            ['df', '-h', home_dir],
            capture_output=True,
            text=True
        )
        
        # Check prerequisites
        prereqs = {}
        for cmd in ['oc', 'podman', 'curl', 'jq']:
            result = subprocess.run(
                ['which', cmd],
                capture_output=True,
                text=True
            )
            prereqs[cmd] = result.returncode == 0
        
        # Check oc ibm-pak
        ibmpak_result = subprocess.run(
            ['oc', 'ibm-pak', '--version'],
            capture_output=True,
            text=True
        )
        prereqs['oc-ibm-pak'] = ibmpak_result.returncode == 0
        
        return jsonify({
            "disk_info": disk_info.stdout,
            "prerequisites": prereqs,
            "home_dir": home_dir,
            "script_path": SCRIPT_PATH
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """Get or update configuration"""
    if request.method == 'GET':
        # Get config file path from query parameter or use default
        config_path = request.args.get('path', CONFIG_FILE)
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return jsonify({"config": f.read()})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        return jsonify({"config": ""})
    
    elif request.method == 'POST':
        try:
            data = request.json
            config_content = data.get('config', '')
            config_path = data.get('path', CONFIG_FILE)
            
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/downloads', methods=['GET', 'POST'])
def downloads():
    """List or start downloads"""
    if request.method == 'GET':
        return jsonify({
            "active": download_manager.get_all_downloads(),
            "history": download_history
        })
    
    elif request.method == 'POST':
        try:
            data = request.json
            component = data.get('component')
            version = data.get('version')
            name = data.get('name')
            filter_pattern = data.get('filter')
            dry_run = data.get('dry_run', False)
            
            # Get configuration parameters
            home_dir = data.get('home_dir')
            final_registry = data.get('final_registry')
            registry_auth_file = data.get('registry_auth_file')
            entitlement_key = data.get('entitlement_key')
            
            if not all([component, version, name]):
                return jsonify({"error": "Missing required fields"}), 400
            
            if not all([home_dir, final_registry, registry_auth_file]):
                return jsonify({"error": "Missing required configuration parameters (home_dir, final_registry, registry_auth_file)"}), 400
            
            download_id = f"{name}-{int(time.time())}"
            result = download_manager.start_download(
                download_id, component, version, name, filter_pattern, dry_run,
                home_dir, final_registry, registry_auth_file, entitlement_key
            )
            
            if "error" in result:
                return jsonify(result), 400
            
            return jsonify(result)
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/downloads/<download_id>', methods=['GET', 'DELETE', 'PATCH'])
def download_detail(download_id):
    """Get, stop, or dismiss a specific download"""
    if request.method == 'GET':
        result = download_manager.get_download_status(download_id)
        if "error" in result:
            return jsonify(result), 404
        return jsonify(result)
    
    elif request.method == 'DELETE':
        result = download_manager.stop_download(download_id)
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result)
    
    elif request.method == 'PATCH':
        # Dismiss download
        result = download_manager.dismiss_download(download_id)
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result)

@app.route('/api/downloads/<download_id>/retry', methods=['POST'])
def retry_download(download_id):
    """Retry a failed download using the script's --retry flag"""
    global download_history
    
    try:
        # Get download info from either active downloads or history
        download = download_manager.downloads.get(download_id)
        if not download:
            # Check history
            for hist in download_history:
                if hist['id'] == download_id:
                    download = hist
                    break
        
        if not download:
            return jsonify({"error": "Download not found"}), 404
        
        # Get configuration from request body (user can modify) or fall back to stored values
        data = request.json or {}
        home_dir = data.get('home_dir') or download.get('home_dir', HOME_DIR)
        final_registry = data.get('final_registry') or download.get('final_registry', 'registry.example.com:5000')
        registry_auth_file = data.get('registry_auth_file') or download.get('registry_auth_file', '/root/.docker/config.json')
        entitlement_key = data.get('entitlement_key') or download.get('entitlement_key')
        
        print(f"[RETRY] Using configuration: home_dir={home_dir}, final_registry={final_registry}")
        
        # Build retry command using the script's --retry flag
        cmd = [
            "bash", SCRIPT_PATH,
            "--component", download['component'],
            "--version", download['version'],
            "--name", download['name'],
            "--retry"  # Use the script's built-in retry mechanism
        ]
        
        if download.get('filter'):
            cmd.extend(["--filter", download['filter']])
        
        # Build environment variables
        env = os.environ.copy()
        env["HOME_DIR"] = home_dir
        env["FINAL_REGISTRY"] = final_registry
        env["REGISTRY_AUTH_FILE"] = registry_auth_file
        if entitlement_key:
            env["ENTITLEMENT_KEY"] = entitlement_key
        
        # Start retry process
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            new_download_id = f"{download['name']}-retry-{int(time.time())}"
            
            # Remove any existing downloads and history entries for this name to avoid duplicates
            with download_manager.lock:
                # Remove from active downloads
                to_remove = [did for did, d in download_manager.downloads.items()
                            if d.get('name') == download['name']]
                for did in to_remove:
                    del download_manager.downloads[did]
                    print(f"Removed old download {did} before retry")
                
                # Remove from history to avoid showing old failed/dismissed entries
                download_history = [h for h in download_history
                                   if h.get('name') != download['name']]
                print(f"Cleaned history for {download['name']}")
                
                download_manager.downloads[new_download_id] = {
                    "id": new_download_id,
                    "component": download['component'],
                    "version": download['version'],
                    "name": download['name'],
                    "filter": download.get('filter'),
                    "process": process,
                    "home_dir": home_dir,
                    "final_registry": final_registry,
                    "registry_auth_file": registry_auth_file,
                    "status": "running",
                    "start_time": datetime.now().isoformat(),
                    "pid": process.pid,
                    "mirror_pid": None,  # Will be captured from log
                    "log_file": f"{home_dir}/{download['name']}/{download['name']}-download.log"
                }
                
                # Start monitoring thread
                threading.Thread(
                    target=download_manager._monitor_download,
                    args=(new_download_id,),
                    daemon=True
                ).start()
            
            return jsonify({"success": True, "download_id": new_download_id, "pid": process.pid})
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/logs/<name>', methods=['GET'])
def get_logs(name):
    """Get log file for a download"""
    try:
        # Get home_dir from query parameter or use default
        home_dir = request.args.get('home_dir', HOME_DIR)
        log_file = f"{home_dir}/{name}/{name}-download.log"
        if not os.path.exists(log_file):
            return jsonify({"error": "Log file not found"}), 404
        
        with open(log_file, 'r') as f:
            return jsonify({"logs": f.read()})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports/<name>', methods=['GET'])
def get_report(name):
    """Get summary report for a download"""
    try:
        # Get home_dir from query parameter or use default
        home_dir = request.args.get('home_dir', HOME_DIR)
        
        # Report is stored directly in home_dir with format: {name}-summary-report.txt
        report_file = f"{home_dir}/{name}-summary-report.txt"
        
        print(f"[REPORT] Looking for report at: {report_file}")
        
        if not os.path.exists(report_file):
            return jsonify({
                "error": f"Report not found. The download may not have completed yet.",
                "path": report_file
            }), 404
        
        with open(report_file, 'r') as f:
            return jsonify({"report": f.read()})
    
    except Exception as e:
        print(f"[REPORT] Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/components', methods=['GET'])
def get_components():
    """Get list of CP4I components"""
    # Return default hardcoded components
    components = [
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
            "versions": ["10.0.8", "10.0.7", "10.0.6"]
        },
        {
            "name": "ibm-mq",
            "description": "MQ Advanced",
            "typical_size": "~8GB",
            "versions": ["9.3.5", "9.3.4", "9.3.3"]
        },
        {
            "name": "ibm-eventstreams",
            "description": "Event Streams",
            "typical_size": "~12GB",
            "versions": ["11.4.0", "11.3.2", "11.3.1"]
        },
        {
            "name": "ibm-app-connect",
            "description": "App Connect Enterprise",
            "typical_size": "~10GB",
            "versions": ["12.0.11", "12.0.10", "12.0.9"]
        },
        {
            "name": "ibm-datapower-operator",
            "description": "DataPower Gateway",
            "typical_size": "~5GB",
            "versions": ["1.11.0", "1.10.3", "1.10.2"]
        }
    ]
    
    return jsonify({"components": components, "source": "default"})

@app.route('/api/validate', methods=['POST'])
def validate_prerequisites():
    """Validate system prerequisites"""
    try:
        result = subprocess.run(
            ['bash', SCRIPT_PATH, '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        return jsonify({
            "valid": result.returncode == 0,
            "output": result.stdout
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Ensure home directory exists
    os.makedirs(HOME_DIR, exist_ok=True)
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)

# Made with Bob
