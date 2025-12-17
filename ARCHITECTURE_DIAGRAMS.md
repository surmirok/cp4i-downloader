# CP4I Downloader - Architecture & Flow Diagrams

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Component Interaction Flow](#component-interaction-flow)
3. [Download Process Flow](#download-process-flow)
4. [Monitoring & Status Flow](#monitoring--status-flow)
5. [Error Handling Flow](#error-handling-flow)
6. [Data Flow Diagram](#data-flow-diagram)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              USER LAYER                                  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      Web Browser (Client)                         │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐ │  │
│  │  │ New        │  │  Active    │  │  History   │  │  Modals    │ │  │
│  │  │ Download   │  │  Downloads │  │  Tab       │  │  & Toasts  │ │  │
│  │  │ Form       │  │  Tab       │  │            │  │            │ │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘ │  │
│  │                                                                    │  │
│  │  HTML/CSS/JavaScript (static/js/app.js, templates/index.html)    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
                                │ HTTP/REST API (JSON)
                                │ GET/POST Requests
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION LAYER                               │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Flask Backend (app.py)                         │  │
│  │                                                                    │  │
│  │  ┌─────────────────────────────────────────────────────────────┐ │  │
│  │  │              DownloadManager Class                           │ │  │
│  │  │  • downloads: dict (active downloads)                        │ │  │
│  │  │  • download_history: list (completed/failed)                 │ │  │
│  │  │  • lock: threading.Lock (thread safety)                      │ │  │
│  │  └─────────────────────────────────────────────────────────────┘ │  │
│  │                                                                    │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │  │
│  │  │   REST API   │  │   Process    │  │   Monitor    │           │  │
│  │  │   Endpoints  │  │   Manager    │  │   Thread     │           │  │
│  │  │              │  │              │  │              │           │  │
│  │  │ /api/        │  │ subprocess   │  │ Log Parser   │           │  │
│  │  │ downloads    │  │ PID Tracker  │  │ Status Check │           │  │
│  │  │ components   │  │ Kill Process │  │ Auto-Dismiss │           │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │  │
│  │                                                                    │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │  │
│  │  │   Report     │  │   Config     │  │   File       │           │  │
│  │  │   Generator  │  │   Manager    │  │   Handler    │           │  │
│  │  │              │  │              │  │              │           │  │
│  │  │ Summary      │  │ Read/Write   │  │ Logs         │           │  │
│  │  │ Statistics   │  │ Validation   │  │ Reports      │           │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
                                │ subprocess.Popen()
                                │ Environment Variables
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           EXECUTION LAYER                                │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              Bash Script (cp4i_downloader.sh)                     │  │
│  │                                                                    │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐ │  │
│  │  │ Validation │  │ OCI Config │  │ Operator   │  │ Image      │ │  │
│  │  │ & Setup    │  │ & Auth     │  │ Fetch      │  │ Mirroring  │ │  │
│  │  │            │  │            │  │            │  │            │ │  │
│  │  │ • Prereqs  │  │ • Registry │  │ • oc       │  │ • oc image │ │  │
│  │  │ • Disk     │  │ • Podman   │  │   ibm-pak  │  │   mirror   │ │  │
│  │  │ • Paths    │  │ • Auth     │  │ • Cases    │  │ • Manifest │ │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘ │  │
│  │                                                                    │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐                  │  │
│  │  │ Logging    │  │ Error      │  │ Cleanup    │                  │  │
│  │  │            │  │ Handling   │  │            │                  │  │
│  │  │ • Detailed │  │ • Retry    │  │ • Temp     │                  │  │
│  │  │ • Progress │  │ • Rollback │  │   Files    │                  │  │
│  │  │ • Summary  │  │ • Report   │  │ • Locks    │                  │  │
│  │  └────────────┘  └────────────┘  └────────────┘                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │
                                │ CLI Commands
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          INFRASTRUCTURE LAYER                            │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │   oc CLI     │  │   Podman     │  │  ibm-pak     │  │  Registry  │ │
│  │              │  │              │  │   Plugin     │  │            │ │
│  │ • Kubernetes │  │ • Container  │  │              │  │ • Private  │ │
│  │ • OpenShift  │  │   Runtime    │  │ • Case Mgmt  │  │ • OCI      │ │
│  │ • Image Ops  │  │ • Image Pull │  │ • Catalog    │  │ • Auth     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    File System Storage                            │  │
│  │  • HOME_DIR: Download artifacts, logs, manifests                 │  │
│  │  • REGISTRY_AUTH_FILE: Authentication credentials                │  │
│  │  • Temporary files: Case data, operator catalogs                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Interaction Flow

```
┌──────────┐                                                    ┌──────────┐
│  User    │                                                    │ Browser  │
│          │                                                    │          │
└────┬─────┘                                                    └────┬─────┘
     │                                                               │
     │ 1. Access Web UI                                             │
     │──────────────────────────────────────────────────────────────▶
     │                                                               │
     │                                                               │
     │◀──────────────────────────────────────────────────────────────
     │ 2. Render HTML/CSS/JS                                        │
     │                                                               │
     │ 3. Fill Form & Submit                                        │
     │──────────────────────────────────────────────────────────────▶
     │                                                               │
     │                                                          ┌────▼─────┐
     │                                                          │  Flask   │
     │                                                          │  Backend │
     │                                                          └────┬─────┘
     │                                                               │
     │                                                               │ 4. Validate
     │                                                               │    Input
     │                                                               │
     │                                                               │ 5. Create
     │                                                               │    Download
     │                                                               │    Entry
     │                                                               │
     │                                                          ┌────▼─────┐
     │                                                          │  Bash    │
     │                                                          │  Script  │
     │                                                          └────┬─────┘
     │                                                               │
     │                                                               │ 6. Execute
     │                                                               │    Download
     │                                                               │
     │                                                               │ 7. Write
     │                                                               │    Logs
     │                                                               │
     │                                                          ┌────▼─────┐
     │                                                          │ Monitor  │
     │                                                          │ Thread   │
     │                                                          └────┬─────┘
     │                                                               │
     │                                                               │ 8. Parse
     │                                                               │    Logs
     │                                                               │
     │                                                               │ 9. Update
     │                                                               │    Status
     │                                                               │
     │ 10. Poll for Updates                                         │
     │──────────────────────────────────────────────────────────────▶
     │                                                               │
     │◀──────────────────────────────────────────────────────────────
     │ 11. Return Status/Progress                                   │
     │                                                               │
     │                                                               │ 12. Detect
     │                                                               │     Complete
     │                                                               │
     │                                                               │ 13. Generate
     │                                                               │     Report
     │                                                               │
     │                                                               │ 14. Move to
     │                                                               │     History
     │                                                               │
     │ 15. View Report/Logs                                         │
     │──────────────────────────────────────────────────────────────▶
     │                                                               │
     │◀──────────────────────────────────────────────────────────────
     │ 16. Display Content                                          │
     │                                                               │
```

---

## Download Process Flow

```
                              START
                                │
                                ▼
                    ┌───────────────────────┐
                    │  User Submits Form    │
                    │  • Component          │
                    │  • Version            │
                    │  • Configuration      │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Validate Input       │
                    │  • Required fields    │
                    │  • Path existence     │
                    │  • Format validation  │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │   Valid?              │
                    └───────────┬───────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                   NO                      YES
                    │                       │
                    ▼                       ▼
        ┌───────────────────┐   ┌───────────────────────┐
        │  Return Error     │   │  Create Download ID   │
        │  Show Toast       │   │  Generate Unique Name │
        └───────────────────┘   └───────────┬───────────┘
                                            │
                                            ▼
                                ┌───────────────────────┐
                                │  Prepare Environment  │
                                │  • Set variables      │
                                │  • Create directories │
                                │  • Setup logging      │
                                └───────────┬───────────┘
                                            │
                                            ▼
                                ┌───────────────────────┐
                                │  Start Bash Script    │
                                │  subprocess.Popen()   │
                                │  • Capture PID        │
                                │  • Redirect output    │
                                └───────────┬───────────┘
                                            │
                                            ▼
                                ┌───────────────────────┐
                                │  Add to Active        │
                                │  Downloads            │
                                │  Status: "running"    │
                                └───────────┬───────────┘
                                            │
                                            ▼
                                ┌───────────────────────┐
                                │  Start Monitor Thread │
                                │  • Watch log file     │
                                │  • Track progress     │
                                │  • Detect completion  │
                                └───────────┬───────────┘
                                            │
                                            ▼
                                ┌───────────────────────┐
                                │  Return Success       │
                                │  Show Toast           │
                                │  Switch to Active Tab │
                                └───────────┬───────────┘
                                            │
                                            ▼
                    ┌───────────────────────────────────┐
                    │     SCRIPT EXECUTION PHASE        │
                    │                                   │
                    │  1. Validate Prerequisites        │
                    │  2. Check Disk Space              │
                    │  3. Setup OCI Configuration       │
                    │  4. Authenticate Registry         │
                    │  5. Fetch Operator Case           │
                    │  6. Generate Manifest             │
                    │  7. Mirror Images                 │
                    │     (or simulate if dry-run)      │
                    │  8. Write Completion Message      │
                    └───────────────┬───────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────────┐
                    │     MONITORING PHASE              │
                    │                                   │
                    │  Every 30 seconds:                │
                    │  • Read log file                  │
                    │  • Check last line                │
                    │  • Update status                  │
                    │  • Calculate progress             │
                    └───────────────┬───────────────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │  Check Last Line              │
                    └───────────────┬───────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐       ┌───────────────────┐       ┌───────────────┐
│ "mirroring    │       │ "error: one or    │       │  Still        │
│  completed"   │       │  more errors"     │       │  Running      │
└───────┬───────┘       └───────┬───────────┘       └───────┬───────┘
        │                       │                           │
        ▼                       ▼                           ▼
┌───────────────┐       ┌───────────────────┐       ┌───────────────┐
│ Status:       │       │ Status: "failed"  │       │ Status:       │
│ "completed"   │       │ Generate Report   │       │ "progressing" │
│ Generate      │       │ Add to History    │       │ Continue      │
│ Report        │       │ Auto-Dismiss      │       │ Monitoring    │
│ Add to        │       └───────────────────┘       └───────────────┘
│ History       │
│ Auto-Dismiss  │
└───────┬───────┘
        │
        ▼
┌───────────────────────┐
│  Wait 5 seconds       │
│  Remove from Active   │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  Available in History │
│  • View Logs          │
│  • View Report        │
│  • Retry              │
└───────────────────────┘
            │
            ▼
          END
```

---

## Monitoring & Status Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    MONITORING THREAD LIFECYCLE                   │
└─────────────────────────────────────────────────────────────────┘

    START (when download begins)
      │
      ▼
┌─────────────────────┐
│ Initialize Monitor  │
│ • Get log file path │
│ • Set check interval│
│ • Start loop        │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────────┐
    │  Sleep 30 sec    │◀─────────────────────┐
    └──────────┬───────┘                      │
               │                              │
               ▼                              │
    ┌──────────────────┐                     │
    │ Check Process    │                     │
    │ Still Running?   │                     │
    └──────────┬───────┘                     │
               │                              │
    ┌──────────▼──────────┐                  │
    │  Process Finished?  │                  │
    └──────────┬──────────┘                  │
               │                              │
       ┌───────┴───────┐                     │
       │               │                     │
      NO              YES                    │
       │               │                     │
       │               ▼                     │
       │    ┌──────────────────┐            │
       │    │  Exit Monitor    │            │
       │    │  Do Final Check  │            │
       │    └──────────────────┘            │
       │                                     │
       ▼                                     │
┌──────────────────┐                        │
│ Read Log File    │                        │
│ Get Last Line    │                        │
└──────────┬───────┘                        │
           │                                 │
           ▼                                 │
┌──────────────────────────────────────┐    │
│  Parse Last Line                     │    │
└──────────┬───────────────────────────┘    │
           │                                 │
    ┌──────┴──────┐                         │
    │             │                         │
    ▼             ▼                         │
┌─────────┐  ┌─────────┐                   │
│ Success │  │  Error  │                   │
│ Pattern │  │ Pattern │                   │
└────┬────┘  └────┬────┘                   │
     │            │                         │
     ▼            ▼                         │
┌─────────┐  ┌─────────┐                   │
│Complete │  │ Failed  │                   │
│ Status  │  │ Status  │                   │
└────┬────┘  └────┬────┘                   │
     │            │                         │
     └────────┬───┘                         │
              │                             │
              ▼                             │
    ┌──────────────────┐                   │
    │ Generate Report  │                   │
    │ Add to History   │                   │
    │ Wait 5 seconds   │                   │
    │ Remove from      │                   │
    │ Active Downloads │                   │
    └──────────────────┘                   │
              │                             │
              ▼                             │
           END                              │
                                            │
    If still running ───────────────────────┘
    (no completion/error detected)


┌─────────────────────────────────────────────────────────────────┐
│                      STATUS TRANSITIONS                          │
└─────────────────────────────────────────────────────────────────┘

    "running"
        │
        │ (log file growing)
        ▼
    "progressing"
        │
        ├──────────────────┬──────────────────┐
        │                  │                  │
        │ (completion)     │ (error)          │ (process ends)
        ▼                  ▼                  ▼
    "completed"        "failed"          "completed"
        │                  │                  │
        │                  │                  │
        └──────────────────┴──────────────────┘
                           │
                           ▼
                    Move to History
                    Auto-Dismiss
```

---

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      ERROR DETECTION FLOW                        │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │  Monitor Thread  │
                    │  Reads Log File  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Get Last Line   │
                    └────────┬─────────┘
                             │
                             ▼
            ┌────────────────────────────────┐
            │ Check for Error Pattern:       │
            │ "error: one or more errors     │
            │  occurred"                     │
            └────────┬───────────────────────┘
                     │
        ┌────────────▼────────────┐
        │  Error Pattern Found?   │
        └────────────┬────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
        YES                     NO
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│ ERROR HANDLING  │    │ Continue Normal │
│                 │    │ Monitoring      │
└────────┬────────┘    └─────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 1. Update Status to "failed"│
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 2. Set End Time             │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 3. Generate Summary Report  │
│    • Error details          │
│    • Partial progress       │
│    • Recommendations        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 4. Add to History           │
│    • Preserve config        │
│    • Store timestamps       │
│    • Link to logs/report    │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 5. Wait 5 Seconds           │
│    (Allow UI to update)     │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 6. Remove from Active       │
│    Downloads                │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 7. Exit Monitor Thread      │
└─────────────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ USER ACTIONS AVAILABLE:     │
│ • View Logs                 │
│ • View Report               │
│ • Retry Download            │
└─────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                    ERROR TYPES & HANDLING                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│  Validation Errors   │
│  (Before Start)      │
└──────────┬───────────┘
           │
           ├─▶ Missing required fields → Show error toast
           ├─▶ Invalid paths → Show error toast
           ├─▶ Invalid format → Show error toast
           └─▶ Duplicate name → Show error toast


┌──────────────────────┐
│  Execution Errors    │
│  (During Download)   │
└──────────┬───────────┘
           │
           ├─▶ Process crash → Detect via returncode
           ├─▶ Authentication failure → Detect in logs
           ├─▶ Network errors → Detect in logs
           ├─▶ Disk space full → Detect in logs
           └─▶ Image mirror errors → Detect "error: one or more errors"


┌──────────────────────┐
│  Recovery Actions    │
└──────────┬───────────┘
           │
           ├─▶ Generate detailed report
           ├─▶ Preserve configuration
           ├─▶ Enable retry with same config
           ├─▶ Provide troubleshooting info
           └─▶ Log complete error context
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW DIAGRAM                               │
└─────────────────────────────────────────────────────────────────────────┘

USER INPUT                    PROCESSING                    OUTPUT/STORAGE
──────────                    ──────────                    ──────────────

┌──────────┐
│ Web Form │
│          │
│ • Name   │──────┐
│ • Config │      │
│ • Paths  │      │
└──────────┘      │
                  │
                  ▼
            ┌─────────────┐         ┌──────────────┐
            │  Validate   │────────▶│  Download    │
            │  & Sanitize │         │  Object      │
            └─────────────┘         │              │
                                    │ • id         │
                                    │ • component  │
                                    │ • version    │
                                    │ • config     │
                                    │ • status     │
                                    │ • timestamps │
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │  Active      │
                                    │  Downloads   │
                                    │  Dictionary  │
                                    └──────┬───────┘
                                           │
                                           │
                  ┌────────────────────────┼────────────────────────┐
                  │                        │                        │
                  ▼                        ▼                        ▼
         ┌────────────────┐      ┌────────────────┐      ┌────────────────┐
         │  Environment   │      │  Bash Script   │      │  Log File      │
         │  Variables     │      │  Execution     │      │                │
         │                │      │                │      │  HOME_DIR/     │
         │ HOME_DIR       │──────▶ • oc commands  │──────▶ name/          │
         │ FINAL_REGISTRY │      │ • ibm-pak      │      │ download.log   │
         │ REGISTRY_AUTH  │      │ • podman       │      │                │
         │ ENTITLEMENT    │      │                │      │ (continuous    │
         └────────────────┘      └────────┬───────┘      │  writing)      │
                                          │              └────────┬───────┘
                                          │                       │
                                          ▼                       │
                                 ┌────────────────┐              │
                                 │  Image Files   │              │
                                 │                │              │
                                 │  HOME_DIR/     │              │
                                 │  name/         │              │
                                 │  • manifests   │              │
                                 │  • catalogs    │              │
                                 │  • images      │              │
                                 └────────────────┘              │
                                                                 │
                                                                 ▼
                                                        ┌────────────────┐
                                                        │  Monitor       │
                                                        │  Thread        │
                                                        │                │
                                                        │ • Parse logs   │
                                                        │ • Track status │
                                                        │ • Detect end   │
                                                        └────────┬───────┘
                                                                 │
                                                                 ▼
                                                        ┌────────────────┐
                                                        │  Status Update │
                                                        │                │
                                                        │ running →      │
                                                        │ progressing →  │
                                                        │ completed/     │
                                                        │ failed         │
                                                        └────────┬───────┘
                                                                 │
                                    ┌────────────────────────────┼────────┐
                                    │                            │        │
                                    ▼                            ▼        ▼
                           ┌────────────────┐         ┌────────────────┐ │
                           │  Summary       │         │  Download      │ │
                           │  Report        │         │  History       │ │
                           │                │         │  List          │ │
                           │  HOME_DIR/     │         │                │ │
                           │  name/         │         │ [{id, status,  │ │
                           │  name-summary- │         │   timestamps,  │ │
                           │  report.txt    │         │   config}]     │ │
                           │                │         │                │ │
                           │ • Statistics   │         └────────┬───────┘ │
                           │ • Timestamps   │                  │         │
                           │ • Errors       │                  │         │
                           │ • Recommendations│                │         │
                           └────────────────┘                  │         │
                                    │                          │         │
                                    └──────────────────────────┘         │
                                                                         │
                                                                         ▼
                                                              ┌────────────────┐
                                                              │  User Views    │
                                                              │                │
                                                              │ • Logs         │
                                                              │ • Reports      │
                                                              │ • History      │
                                                              │ • Retry        │
                                                              └────────────────┘
```

---

## Legend

### Symbols Used
- `│` `─` `┌` `└` `┐` `┘` : Box drawing characters
- `▼` `▶` `◀` : Flow direction arrows
- `→` : Data/control flow
- `├` `┤` `┬` `┴` `┼` : Connection points

### Status Values
- **running**: Initial state when download starts
- **progressing**: Active mirroring detected
- **completed**: Successfully finished
- **failed**: Error detected or non-zero exit
- **dismissed**: Manually stopped by user

### Key Components
- **Flask Backend**: Python application managing downloads
- **Bash Script**: Executes actual download operations
- **Monitor Thread**: Background thread tracking progress
- **Download Manager**: Central state management
- **File System**: Persistent storage for logs/reports

---

*Generated for CP4I Downloader v2.0*