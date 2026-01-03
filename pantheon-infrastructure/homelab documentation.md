# Cerberus

# **OPNsense Home Network Configuration Documentation (Procedural Build Guide)**

**Purpose**: This document is a *reproducible build guide*. Every section contains **explicit UI paths, field values, and ordering constraints** so the environment can be rebuilt from scratch after a factory reset or hardware replacement.

---

## **0\. Scope & Assumptions**

* Firewall: **OPNsense (Cerberus)**  
* Switch: **Cisco SG350-28P (Axon)**  
* WAN: Starlink (primary), Fiber (secondary – optional)  
* VLAN trunk via **em0** only  
* Security model: **Zero‑Trust Lite** (no lateral movement by default)  
  ---

  ## **1\. Initial OPNsense Installation**

  ### **1.1 Setup Wizard**

**UI Path:** `System → Wizard`

* **WAN (em6)**  
  * IPv4: DHCP  
  * IPv6: Track Interface (Prefix ID 0\)  
* **Secondary WAN (em5)**  
  * Leave unconfigured initially  
* **LAN (em0)**  
  * IPv4: *None*  
  * Purpose: VLAN trunk only  
* **Admin**  
  * Set strong password  
  * Enable 2FA later under `System → Access → Users`

Apply and complete wizard.

---

## **2\. VLAN Creation (Authoritative)**

### **2.1 Create VLANs**

**UI Path:** `Interfaces → Other Types → VLAN`

Create the following **on parent em0**:

| VLAN ID | Name |
| ----- | ----- |
| 10 | EXPOSED |
| 20 | USER |
| 30 | IOT |
| 40 | GUEST |
| 50 | UNTRUSTED |
| 60 | SERVERS |
| 99 | MGMT |

Save.

### **2.2 Assign VLAN Interfaces**

**UI Path:** `Interfaces → Assignments`

Assign each VLAN, then click into each interface and:

* ✔ Enable Interface  
* IPv4 Configuration: **Static IPv4**  
* IPv6 Configuration: **None** (initially)

Apply each interface **one at a time**.

| VLAN ID | Name | Subnet | Status | Purpose |
| ----- | ----- | ----- | ----- | ----- |
| 10 | EXPOSED | 192.168.10.0/24 | ✅ Active | Public-facing / DMZ-style devices |
| 20 | USER | 192.168.20.0/24 | ✅ Active | Trusted user devices (Ares, Wi-Fi clients) |
| 30 | IOT | 192.168.30.0/24 | ✅ Active | IoT devices |
| 40 | GUEST | 192.168.40.0/24 | ✅ Active | Guest Wi-Fi |
| 50 | UNTRUSTED | 192.168.50.0/24 | ✅ Active | Quarantine / testing |
| 60 | SERVERS | 192.168.60.0/24 | 🟡 Created (no hosts yet) | Internal servers (Atlas, Prometheus) |
| 99 | MGMT | 192.168.99.0/24 | ✅ Active | Network & infrastructure management |

⚠️ **Never parent VLANs to WAN interfaces**.

### **Design Notes**

* **SERVERS (VLAN 60\)** is intentionally *not exposed* to USER or Wi-Fi.

* **MGMT (VLAN 99\)** is *hard-isolated* and only reachable from wired admin ports.

* USER Wi-Fi intentionally **cannot access** MGMT or switch/AP admin panels.

  ---

  ## **3\. Core Services**

  ### **3.1 DHCP**

**UI Path:** `Services → DHCPv4`

For each VLAN:

* Enable DHCP  
* Range: `.100 – .200`  
* Gateway: VLAN interface IP

Save per interface.

---

### **3.2 DNS Resolver (Unbound)**

**UI Path:** `Services → Unbound DNS → General`

Enable:

* ✔ Enable Unbound  
* ✔ Listen Interfaces: **All**  
* ✔ Register DHCP leases  
* ✔ Register static mappings

Advanced (temporary diagnostics only):

* ✔ Prefetch Support  
* ✔ Prefetch DNS Key Support  
* ✔ Log Queries  
* Log Verbosity: **2**

⚠️ Disable logging after valida   tion.

---

### **3.3 System DNS**

**UI Path:** `System → Settings → General`

* DNS Servers:  
  * `1.1.1.1`  
  * `8.8.8.8`  
* ❌ Uncheck **Allow DNS server list to be overridden**

Save.

---

## **4\. Firewall Aliases (MANDATORY)**

**UI Path:** `Firewall → Aliases`

### **4.1 PrivateNetworks**

* Type: Network(s)  
* Values:  
  * `10.0.0.0/8`  
  * `172.16.0.0/12`  
  * `192.168.0.0/16`

  ---

  ### **4.2 Host Aliases**

Create the following as needed:

| Alias | IP | VLAN |
| ----- | ----- | ----- |
| WebServer | 192.168.10.10 | EXPOSED |
| Printer | 192.168.30.10 | IOT |
| IPCameras | 192.168.50.10‑12 | UNTRUSTED |

---

---

## **5\. Firewall Rules (CRITICAL ORDER)**

### **5.1 Universal DNS Rule Pattern**

For **every VLAN interface**:

* Action: Pass  
* Protocol: TCP/UDP  
* Source: `<VLAN> net`  
* Destination: **This Firewall**  
* Destination Port: **53 → 53**

🚫 Never use `any → 53`.

---

### **5.2 USER VLAN (20)**

**UI Path:** `Firewall → Rules → USER`

Order matters:

1. Allow DNS → Firewall  
2. Allow USER → WebServer (443)  
3. Allow USER → Printer  
4. Pass USER → \!PrivateNetworks (Internet‑only)  
   ---

   ### **5.3 EXPOSED / IOT / GUEST**

Pattern:

1. Allow DNS → Firewall  
2. Pass → \!PrivateNetworks

No internal access permitted.

---

### **5.4 MGMT VLAN (99)**

Explicit only:

* MGMT → This Firewall (443)  
* MGMT → Axon (192.168.99.2, 443\)  
* Block everything else (implicit)  
  ---

  ## **8\. Stable Baseline Declaration**

At this point:

* VLAN isolation works  
* DNS resolves correctly  
* MGMT is locked down  
* System is reproducible

🔒 **Do not add VPN / Multi‑WAN until a config backup is taken**.

---

*End of procedural build guide*

---

# Tab 9

##  **Network Change Log – Admin Access & Servers Prep**

### **Date**

2025-12-29

### **Context**

After stabilizing the VLAN-segmented network, additional changes were required to restore Wi‑Fi connectivity and prepare for server expansion (Atlas \+ Prometheus) while maintaining a zero‑trust posture.

---

## **✅ Decisions Made**

### **1\. Admin Access Strategy (FINAL)**

We will use **Option A: Dedicated MGMT SSID**.

**Rationale:**

* Preserves zero‑trust between USER/Wi‑Fi and infrastructure  
* Avoids weak, exception-based firewall rules  
* Aligns with enterprise best practice

**Outcome:**

* Admin access is intentionally *not available* from standard Wi‑Fi  
* Infrastructure is only reachable from:  
  * Wired MGMT VLAN  
  * Dedicated MGMT Wi‑Fi SSID (to be created)  
  * Future VPN (WireGuard)

---

## **🔧 Changes Performed (Axon \+ AP Recovery)**

### **Axon (Cisco SG350)**

* **GE6** reassigned to **VLAN 20 (USER)** to restore AP uplink  
* APs rebooted  
* Result: Wi‑Fi internet access restored

This confirmed:

* VLAN 20 routing, NAT, DHCP, and DNS are functional  
* APs correctly bridge USER traffic when placed on VLAN 20

---

## **🔍 Current Access Behavior (Verified)**

| Source Device | Network | Access to Atlas | Expected |
| :---- | :---- | :---- | :---- |
| **Ares (wired)** | USER (20) | ✅ Yes | Correct |
| **Nomad (Wi‑Fi)** | USER (20) | ❌ No | Correct |

Reason:

* USER VLAN is intentionally blocked from infrastructure/admin access  
* Atlas is currently on USER VLAN only as a temporary measure

---

## **🧱 Current State of Atlas**

* Connected to **GE1 (USER VLAN 20\)**  
* Reachable from Ares  
* Not reachable from Wi‑Fi clients

⚠️ **This is temporary.** Atlas will be migrated once physical access is available.

---

## **🧠 Planned Network Architecture (Next Phase)**

### **SERVERS VLAN (60)**

Purpose:

* Host internal infrastructure and compute  
* No direct USER or GUEST access

Planned residents:

* **Atlas** (Unraid NAS)  
* **Prometheus** (Compute / Docker / AI)

### **Access Model**

* **MGMT (99)** → Full admin access  
* **USER (20)** → Explicit, limited service access only  
* **Wi‑Fi** → No admin access by default

---

## **📅 Planned Next Steps**

### **Step 1 – Create MGMT SSID (NEXT)**

* Hidden SSID mapped to **VLAN 99**  
* Strong WPA2/WPA3 credentials  
* Used only for administration

### **Step 2 – Move Atlas**

* Re-cable Atlas to **SERVERS VLAN port**  
* Verify IP assignment (192.168.60.x)  
* Update Unraid network settings if needed  
* Add firewall rules:  
  * MGMT → Atlas (admin)  
  * USER → Atlas (only required services)

### **Step 3 – Bring Prometheus Online**

* Assign Prometheus to SERVERS VLAN  
* No USER or GUEST lateral access  
* Managed exclusively via MGMT

---

## **🛑 Stopping Point Declaration**

**Status:** Network stable and secure

No further changes should be made until:

* MGMT SSID is created  
* Atlas is intentionally migrated to SERVERS VLAN

This prevents accidental lockouts and configuration drift.

---

*End of documented section*

# Axon

## **Cisco SG350 (Axon) Configuration**

### **6.1 VLANs and Port Grouping Strategy**

Ports are grouped logically by VLAN to simplify troubleshooting and scaling.

* ### **USER VLAN (20)**

  * **GE1** → Atlas (temporary)  
  * GE2 → Atlas (temporary)

  * **GE6** → AP uplink (USER \+ GUEST via trunk; temp)

  * **GE12**

  * **GE13**

  * **GE14**

* ### **IOT VLAN (30)**

  * **GE3**

  * **GE4**

  * **GE15**

  * **GE16**

* ### **GUEST VLAN (40)**

  * **GE5**  
  * **GE17**

* ### **UNTRUSTED VLAN (50)**

  * **GE6 (future reassignment planned)**

  * **GE18**

* ### **SERVERS VLAN (60)**

  * **GE7**

  * **GE19**

* ### **MGMT VLAN (99)**

  * **GE2** → Switch management / admin access

* ### **TRUNK**

  * **GE24** → Cerberus (`em0`)

    * Tagged VLANs: 10,20,30,40,50,60,99

    * Native VLAN: 1 (unused)  
* 

---

## **🖧 SERVERS VLAN – Design & Intent**

### **Purpose**

The SERVERS VLAN isolates **infrastructure systems** from user devices while allowing controlled service access.

This VLAN hosts:

* Atlas (NAS)

* Prometheus (compute / AI / apps)

---

### **Configuration**

* VLAN ID: *(document actual ID here)*

* Subnet: *(document subnet here)*

* Ports:

  * Port 7 → Atlas

  * Port 19 → Prometheus

---

### **Allowed Traffic**

* MGMT → SERVERS (administration)

* SERVERS → Atlas (NFS/SMB internal)

* SERVERS → Internet (updates, containers)

### **Blocked Traffic**

* USER → SERVERS (no direct access)

* GUEST → SERVERS

* UNTRUSTED → SERVERS

# Access Points

## **7\. Wireless AP (E8450 \+ RE9000)**

* Axon port → trunk VLANs 20 & 40 only  
* OpenWRT:  
  * Disable DHCP/NAT  
  * Create eth0.20 & eth0.40  
  * Bridge to SSIDs

  ### **Current State (Intentional)**

* AP is connected to **GE6**

* GE6 is currently **VLAN 20 (USER)** only

* Result:

  * ✅ Internet access restored

  * ❌ No access to admin panels from Wi-Fi (expected & desired)

  ### **Security Rationale**

This enforces **Zero-Trust-Lite**:

* Wi-Fi clients are treated as USER devices

* Admin access requires **wired MGMT VLAN**

* Prevents credential theft via compromised Wi-Fi clients

# Atlas

# **Atlas NAS (Unraid) – Configuration & Build Guide**

## **Purpose**

This document defines the **exact, reproducible steps** required to deploy **Atlas**, the homelab’s authoritative NAS, from bare metal to a stable production-ready state.

Atlas is **storage-first**, **headless**, and **compute-agnostic**, designed to integrate cleanly with the **Cerberus (OPNsense)** and **Axon (Cisco SG350)** network.

**Assumption:** Network v1.0 is stable and operational before beginning.

---

## **0\. Role Definition (Authoritative)**

| Item | Value |
| ----- | ----- |
| Hostname | Atlas |
| Role | Central NAS / Media / Backups |
| OS | Unraid |
| Primary Users | Household devices |
| Compute Role | ❌ None |
| Management Model | Web UI only (headless) |
| VLAN (Final) | SERVERS |
| VLAN (Temporary) | USER (documented exception) |

**Design Rule:**  
 Atlas provides **storage and data services only**.  
 No AI, no heavy containers, no GPU workloads.

---

## **1\. Hardware Baseline**

### **1.1 Chassis & Controller**

| Component | Value |
| ----- | ----- |
| Server | Dell PowerEdge R530 |
| RAID Controller | Dell PERC H730 |
| Controller Mode | **HBA / Non-RAID (Pass-through)** |

⚠️ **Critical:**  
 Unraid **requires direct disk access**.  
 The PERC H730 **must not** present RAID volumes.

---

### **1.2 Disk Inventory**

| Count | Size | Type | Purpose |
| ----- | ----- | ----- | ----- |
| 6 (installed) | 4 TB | HDD | Data disks |
| 2 (future) | 4 TB | HDD | Data expansion |
| 2 (planned) | 4 TB | HDD | Parity |
| 1 | 250 GB | NVMe | Cache (BTRFS) |

All disks **must appear individually** in Unraid.

---

## **2\. Unraid Installation**

### **2.1 USB Creation**

1. Download **Unraid USB Creator**

2. Select **latest stable Unraid**

3. Write to USB (GUID-bound license)

4. Label USB clearly (e.g., `UNRAID_ATLAS`)

---

### **2.2 Initial Boot**

1. Insert USB into Atlas

2. Boot server

3. Allow DHCP assignment

4. Discover IP via:

   * Cerberus DHCP leases **or**

   * Temporary local monitor

Access UI:

 `http://<assigned-ip>`

5. 

Atlas is now **headless** after this step.

---

## **3\. Network Configuration**

### **3.1 VLAN Placement**

#### **Current (Temporary – Documented Exception)**

| Interface | VLAN | Reason |
| ----- | ----- | ----- |
| NIC 1 | USER (20) | License activation, SMB access during recovery |

This was required due to:

* MGMT VLAN DNS restrictions

* Prior admin lockout recovery

---

#### **Final Intended Placement (Authoritative)**

| Interface | VLAN | Purpose |
| ----- | ----- | ----- |
| NIC 1 | SERVERS | SMB / NFS / data services |
| NIC 2 | MGMT | Administration only |

**Why Atlas does NOT stay on USER:**

* Prevents lateral movement

* Enforces zero-trust-lite

* Matches enterprise NAS patterns

---

### **3.2 Network Settings**

**UI Path:** `Settings → Network Settings`

| Setting | Value |
| ----- | ----- |
| IPv4 | DHCP (initial) |
| IPv6 | Disabled |
| Gateway | Cerberus |
| Static IP | Later via DHCP reservation |

---

## **4\. Disk Assignment & Array Creation**

### **4.1 Disk Assignment**

**UI Path:** `Main → Array Devices`

1. Assign **data disks**

2. Leave **parity unassigned** (current state)

3. Assign **NVMe** to Cache Pool

⚠️ Parity cannot be added *after* disks are already assigned without rebuilding.  
 This is a known, accepted temporary state.

---

### **4.2 Array Start & Format**

1. Start array

2. Confirm formatting

3. Wait for completion

---

### **4.3 Parity Validation**

* Run **Read-Check (non-correcting)**

* Confirm **zero errors**

---

## **5\. Cache Configuration**

### **5.1 Cache Pool**

* File system: **BTRFS**

* Format: Auto (default)

* Purpose:

  * Appdata

  * Docker layers

  * Write acceleration

No filesystem change required.

---

## **6\. Share Configuration**

### **6.1 Global Share Settings**

**UI Path:** `Settings → Global Share Settings`

| Setting | Value |
| ----- | ----- |
| User Shares | Enabled |
| Disk Shares | Disabled |
| Allocation | High-water |
| Min Free Space | 20–50 GB |

---

### **6.2 Split Level (Recommended)**

| Share Type | Split Level |
| ----- | ----- |
| Media | Automatic |
| Documents | Automatic |
| Backups | Automatic |
| Appdata | Manual (tight) |

**Rule:**  
 Use **Automatic** unless you know exactly why you shouldn’t.

---

## **7\. Security Model (Zero-Trust Lite)**

### **7.1 Current Controls**

* ❌ No WAN exposure

* ❌ No port forwarding

* ✅ Access only via internal VLANs

* ✅ Firewall-enforced access paths

---

### **7.2 Future Hardening (Planned)**

* Move admin UI fully to **MGMT VLAN**

* HTTPS \+ certificate

* SMB access limited by VLAN

* Disable unused services

---

## **8\. Licensing**

### **8.1 License Activation**

**Requirements:**

* Working DNS

* Internet access

**Known Issue:**

* MGMT VLAN blocked DNS initially

* Resolved by temporary USER VLAN placement

This is **documented and accepted**.

---

## **9\. Protocol Model (Authoritative)**

### **9.1 SMB – Human Access**

Used by:

* Nomad

* Ares

* Family devices

Shares:

* `documents`

* `media`

* `photos`

* `backups`

* `scans`

Characteristics:

* User authentication

* Familiar UX

* Read/write controls

---

### **9.2 NFS – Server / Compute Access**

Used by:

* Prometheus

* Linux VMs

* Containers

Exports:

* `/exports/media`

* `/exports/scans`

* `/exports/nextcloud-data`

Prometheus mounts **read/write only where required**.

---

## **10\. What Atlas Does NOT Do**

❌ Run AI workloads  
 ❌ Run GPU workloads  
 ❌ Host VM disks  
 ❌ Cache AI models  
 ❌ Perform heavy compute

Atlas is **durable storage**, not a compute node.

---

## **11\. Validation Checklist**

* Disks visible individually

* Array started

* Cache formatted (BTRFS)

* Shares created

* SMB accessible

* Read-check clean

* Parity assigned (future)

---

## **12\. Known Issues & Lessons Learned**

### **RAID Controllers**

* PERC defaults to RAID

* Must be switched to pass-through

### **VLAN DNS Dependency**

* License activation requires DNS

* MGMT VLAN must explicitly allow DNS if used

---

## **13\. Next Steps**

* Assign parity when remaining drives installed

* Move Atlas fully to SERVERS VLAN

* Lock down MGMT access

* Mount Atlas exports on Prometheus

* Deploy Jellyfin on Prometheus (not Atlas)

# Media Configuration

Media  
Perfect. Below are two full, drop-in sections you can paste directly into your master document:

1\. Media Architecture & Data Flow (authoritative decision)

2\. Atlas Media Services Setup (SMB \+ NFS) — procedural, reproducible

They are written to match the same depth and tone as your network sections.

\---

📘 Media Architecture & Data Flow (Authoritative)

Purpose

This section defines where media lives, how it is accessed, and how compute services interact with stored data. These decisions are intentional and form part of the lab’s zero-trust design.

\---

System Roles

Atlas (NAS – SERVERS VLAN)

Role:  
System of record for all persistent data.

Responsibilities:

Store all media and user data

Serve data to clients and services

Maintain parity, integrity, and backups

Data stored on Atlas:

Movies

TV Shows

Music

Photos

Family documents

Backups

Application metadata (where appropriate)

Atlas is stateful and data-critical.

\---

Prometheus (Compute – SERVERS VLAN)

Role:  
Compute and service host only.

Responsibilities:

Run containers and services

Consume media from Atlas

Perform transcoding, indexing, AI tasks

What Prometheus does NOT do:

It does not permanently store media

It is not a backup target

It is not user-facing for file storage

Prometheus is stateless / rebuildable.

\---

Media Flow Model

\[ Atlas (Storage) \]  
        │  
        │  NFS (preferred) / SMB  
        │  
\[ Prometheus (Services) \]  
        │  
        │  HTTPS / Streaming  
        │  
\[ USER Devices \]

Key Rules

USER devices access media only via Atlas SMB

Services access media only via Prometheus

USER devices never access Prometheus directly

Prometheus never becomes the sole holder of data

\---

Security Implications

Atlas is protected behind SERVERS VLAN firewall rules

Prometheus can be rebuilt without data loss

A compromised service does not compromise storage

Zero-trust boundaries are preserved

\---

Final Decision (Locked)

\> All media lives on Atlas. Prometheus consumes media but never owns it.

\---

📘 Atlas Media Services Setup (SMB \+ NFS)

This section documents the exact steps to expose media from Atlas to:

Family devices (SMB)

Prometheus (NFS)

\---

1️⃣ Share Layout (Atlas)

Required Shares

Share Name	Purpose

media	Movies, TV, music  
photos	Family photos  
documents	Family documents  
backups	Device backups  
appdata	Application metadata (optional)  
system	Unraid system data

\---

2️⃣ SMB Configuration (Family Access)

Enable SMB

Settings → SMB

Enable SMB: ✅

Workgroup: WORKGROUP (or your preference)

SMB Security: Yes

Local master: Auto

Apply changes.

\---

SMB Share Settings (Per Share)

For media, photos, documents:

Export: Yes

Security: Private

SMB Access:

alex: Read/Write

vanessa: Read/Write

family: Read (or RW if desired)

⚠️ Do not use “Public” shares.

\---

3️⃣ NFS Configuration (Prometheus Access)

Enable NFS

Settings → NFS

Enable NFS: ✅

NFSv4: ✅

Security: Private

Apply.

\---

NFS Export (media share)

Shares → media → NFS Security Settings

Export: Yes

Host(s):

192.168.60.0/24 (SERVERS VLAN)

Access:

Read-only (recommended initially)

Security:

Private

This ensures:

Prometheus can read media

Prometheus cannot delete media accidentally

\---

4️⃣ Prometheus Mount (Future Step)

On Prometheus:

mkdir \-p /mnt/media  
mount \-t nfs 192.168.60.X:/mnt/user/media /mnt/media

Later:

Add to /etc/fstab or Docker bind mounts

Document persistent mounts

\---

5️⃣ Validation Checklist

\[ \] USER device can browse Atlas via SMB

\[ \] USER device cannot access Prometheus

\[ \] Prometheus can read media over NFS

\[ \] Prometheus cannot modify media (if RO)

\[ \] Atlas parity remains healthy

\---

6️⃣ Known Risks & Mitigations

Risk	Mitigation

Accidental media deletion	RO NFS  
Service compromise	VLAN isolation  
Prometheus failure	Atlas remains intact  
Credential leakage	Private SMB shares

\---

📝 To-Do (Media & Services – Updated)

\[ \] Confirm Atlas shares exist and are secured

\[ \] Finalize SMB permissions per user

\[ \] Enable NFS on Atlas

\[ \] Export media share to SERVERS VLAN

\[ \] Mount media on Prometheus

\[ \] Decide RO vs RW for services

\[ \] Document Jellyfin / Plex deployment

\[ \] Validate streaming performance

\[ \] Update backup strategy for media

\---

🛑 Stopping Point (Media Section)

State:

Architecture decisions finalized

Atlas configured as storage authority

Prometheus not yet consuming media

Safe to pause here.

# 📦 Nextcloud on Atlas (Migration-Safe)

📦 Nextcloud on Atlas (Migration-Safe, Prometheus-Ready)  
Goal:  
Deploy Nextcloud on Atlas today in a way that allows a clean lift-and-shift to Prometheus later with no data migration and no reconfiguration.  
0️⃣ Preconditions (Verify Before Proceeding)  
Confirm these already exist on Atlas:  
Shares (SMB/NFS)  
appdata  
nextcloud-data  
backups (optional but recommended)  
If not, create them now:  
Unraid UI → Shares → Add Share  
Use default settings  
Export via SMB (private)  
1️⃣ Decide the Nextcloud Stack (Locked Decision)  
We will use:  
Component  
Choice  
Reason  
Nextcloud  
LinuxServer.io container  
Stable, well-documented  
Database  
MariaDB container  
Required for scale & migration  
Web  
Built into Nextcloud container  
Simple, portable  
Reverse Proxy  
Not now  
Added later on Prometheus  
Storage  
Atlas (bind-mounted)  
Authoritative data  
🚫 Do NOT use:  
SQLite  
Snap installs  
Unraid “plugin” versions  
2️⃣ Create Appdata Structure (Explicit)  
On Atlas, ensure the following directories exist:  
Copy code  
Text  
/mnt/user/appdata/nextcloud  
/mnt/user/appdata/mariadb-nextcloud  
/mnt/user/nextcloud-data  
You can create these via:  
SMB from Nomad/Ares or  
Unraid terminal:  
Copy code  
Bash  
mkdir \-p /mnt/user/appdata/nextcloud  
mkdir \-p /mnt/user/appdata/mariadb-nextcloud  
mkdir \-p /mnt/user/nextcloud-data  
3️⃣ Deploy MariaDB (First – Required)  
Unraid → Apps → Search: “MariaDB (linuxserver)”  
MariaDB Configuration  
Set these exactly:  
Paths  
/config → /mnt/user/appdata/mariadb-nextcloud  
Environment Variables  
MYSQL\_ROOT\_PASSWORD → strong password  
MYSQL\_DATABASE → nextcloud  
MYSQL\_USER → nextcloud  
MYSQL\_PASSWORD → strong password  
TZ → your timezone  
Network  
Bridge (default)  
✅ Apply and wait until container shows “running”  
4️⃣ Deploy Nextcloud  
Unraid → Apps → Search: “Nextcloud (linuxserver)”  
Nextcloud Configuration  
Paths  
Container Path  
Host Path  
/config  
/mnt/user/appdata/nextcloud  
/data  
/mnt/user/nextcloud-data  
Environment Variables  
PUID → 99  
PGID → 100  
TZ → your timezone  
Network  
Bridge  
✅ Apply and start container  
5️⃣ Initial Nextcloud Web Setup  
From Nomad or Ares:  
Copy code

http://atlas-ip:port  
(Use the port shown in Unraid, usually 444 or 8080\)  
Web Installer Settings  
Admin Account  
Username: admin (or your choice)  
Password: strong  
Database  
Database user: nextcloud  
Database password: (from MariaDB)  
Database name: nextcloud  
Database host: mariadb-nextcloud (container name)  
⚠️ DO NOT change the data directory  
It must remain /data  
Click Install  
6️⃣ Validate Data Placement (Critical)  
After setup completes:  
On Atlas, confirm:  
Copy code  
Text  
/mnt/user/nextcloud-data/  
contains:  
files/  
appdata\_\*/  
uploads/  
If data is here → ✅ correct  
If data is inside /mnt/user/appdata/nextcloud → ❌ stop and fix  
7️⃣ Permissions Sanity Check (If Needed)  
If uploads fail later:  
Copy code  
Bash  
chown \-R 99:100 /mnt/user/nextcloud-data  
chown \-R 99:100 /mnt/user/appdata/nextcloud  
Restart both containers.  
8️⃣ What This Enables Later (Important)  
Because of how this is set up:  
When Prometheus Takes Over  
You will:  
Stop containers on Atlas  
Mount:  
/mnt/user/nextcloud-data via NFS  
/mnt/user/appdata/nextcloud via NFS  
Start identical containers on Prometheus  
Nextcloud comes up unchanged  
No:  
Reinstall  
Re-upload  
Permission surgery  
9️⃣ Explicit Non-Goals (Documented)  
❌ No external access yet  
❌ No reverse proxy yet  
❌ No HTTPS yet  
❌ No cloud offloading yet  
Those are Phase 2 tasks after Prometheus is stable.  
🛑 Stopping Point (Save This)  
Status:  
Atlas shares finalized  
Nextcloud deployed in migration-safe layout  
Data already moving into Atlas safely  
Ready for Prometheus takeover later  
Safe to pause here.  
Next Logical Steps (When You’re Ready)  
Add user accounts in Nextcloud  
Tune upload size limits  
Decide: Photos auto-upload from phones  
Then → torrent stack (last, as planned)

# Hardening Guide

# **Nextcloud on Atlas – Configuration & Hardening Guide**

This section will document the **Nextcloud setup** on Atlas, covering everything from installation, configuration, security hardening, to external storage integration and performance tuning.

---

## **1\. Data Directory Setup (Clean Installation)**

Ensure Nextcloud is correctly pointed at the **data directory**:

**Create a new, empty data directory**:

 `/mnt/user/nextcloud-data`

1. 

**Verify directory permissions**:

 `chown -R abc:abc /mnt/user/nextcloud-data`

2. 

**Edit `config.php`** to reflect the data directory:

 `'datadirectory' => '/mnt/user/nextcloud-data',`

3. 

**Create `.ncdata` file** in the data directory (this is Nextcloud’s signature file for data management):

 `echo "# Nextcloud data directory" > /mnt/user/nextcloud-data/.ncdata`

4. 

---

## **2\. Docker Containers: Deploying Nextcloud & MariaDB**

### **Step 1: Deploy MariaDB (Database)**

Run the following command to deploy MariaDB:

`docker run \`  
  `-d \`  
  `--name='MariaDB-Nextcloud' \`  
  `--net='bridge' \`  
  `-e 'MARIADB_ROOT_PASSWORD'='CodexStructuredKnowledgeCollection' \`  
  `-e 'MARIADB_DATABASE'='nextcloud' \`  
  `-e 'MARIADB_USER'='nextcloud' \`  
  `-e 'MARIADB_PASSWORD'='ThunderComesBeforeStorms' \`  
  `-v '/mnt/user/appdata/mariadb-nextcloud/data/':'/var/lib/mysql':'rw' \`  
  `-v '/mnt/user/appdata/mariadb-nextcloud/config':'/etc/mysql/conf.d':'rw' \`  
  `--memory=2G 'mariadb'`

Verify MariaDB is running:

`docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"`

### **Step 2: Deploy Nextcloud**

Run the following for Nextcloud (adjusting ports as necessary):

`docker run \`  
  `-d \`  
  `--name='Nextcloud' \`  
  `--net='nextcloud_net' \`  
  `-p '8080:80' \`  
  `-e 'MYSQL_PASSWORD'='ThunderComesBeforeStorms' \`  
  `-e 'MYSQL_DATABASE'='nextcloud' \`  
  `-e 'MYSQL_USER'='nextcloud' \`  
  `-e 'MYSQL_HOST'='MariaDB-Nextcloud' \`  
  `-v '/mnt/user/appdata/nextcloud/config':'/config':'rw' \`  
  `-v '/mnt/user/nextcloud-data':'/data':'rw' \`  
  `--memory=2G 'lscr.io/linuxserver/nextcloud'`

**Explanation:**

* `8080:80`: Exposes Nextcloud web UI on port 8080 (for now)

* **Data volume** is mapped to `/mnt/user/nextcloud-data`

* **Config volume** is mapped to `/mnt/user/appdata/nextcloud/config`

Verify Nextcloud container:

`docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"`

Access Nextcloud UI:

`http://<Atlas-IP>:8080`

---

## **3\. Configuring Redis for File Locking & Performance**

Nextcloud supports **transactional file locking** through **Redis**. This ensures:

* Stable performance under load

* Correct file synchronization

### **Step 1: Install Redis**

Run the following to deploy Redis as a container:

`docker run \`  
  `-d \`  
  `--name='Redis-Nextcloud' \`  
  `--net='nextcloud_net' \`  
  `--memory=256M \`  
  `'redis:latest'`

Verify Redis is running:

`docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"`

### **Step 2: Configure Redis in `config.php`**

Edit `config.php` (host-side recommended):

`nano /mnt/user/appdata/nextcloud/config/config.php`

Add the following to enable **Redis for file locking**:

`'memcache.local' => '\OC\Memcache\APCu',`  
`'memcache.locking' => '\OC\Memcache\Redis',`  
`'redis' => [`  
  `'host' => 'Redis-Nextcloud',`  
  `'port' => 6379,`  
`],`

### **Step 3: Restart Nextcloud**

After saving `config.php`:

`docker restart nextcloud`

Verify there are no errors after restart and check Admin → Overview for **file locking** and **memcache** status.

---

## **4\. Database Configuration and Error Fixes**

### **Missing Indices & Mimetype Migration**

Fix database performance issues:

`docker exec -u abc nextcloud php /app/www/public/occ db:add-missing-indices`  
`docker exec -u abc nextcloud php /app/www/public/occ maintenance:repair --include-expensive`

---

## **5\. External Storage Configuration**

Nextcloud should be configured to use existing storage on Atlas via **External Storage** (SMB or NFS).

1. **Enable External Storage support** app

2. **Add mounts**:

   * `/mnt/user/documents` → Documents

   * `/mnt/user/photos` → Photos

   * `/mnt/user/media` → Media

---

## **6\. Known Issues & Troubleshooting**

### **1\. MariaDB Version Warning**

MariaDB 12.x is newer than Nextcloud’s recommended 10.6–11.8. This **works fine**, but note:

* Future Nextcloud updates may be slow to officially validate it.

* **No action required** unless you hit issues.

### **2\. Memory Cache Missing**

Add a **Redis cache** (already done) to improve performance under heavy use.

---

## **📝 To-Do**

* Complete Nextcloud database setup with External Storage

* Finalize security hardening (HTTPS proxy, Redis full config)

* Document usage and backup strategies

# Prometheus

# **🖥 Prometheus Initialization Procedure (SERVERS Compute Node)**

This section documents the **initial bring-up, OS installation, and baseline configuration** of **Prometheus**, the centralized compute node for heavy workloads including 3D scanning, AI, and virtualization.

---

## **🎯 Purpose**

Prometheus is designed to:

* Host virtualization (KVM/QEMU)

* Run compute-heavy workloads

* Remain isolated from user devices

* Avoid data ownership (storage lives on Atlas)

Prometheus is **not** a workstation and **not** a storage server.

---

## **🧱 Role & Network Placement (Authoritative)**

| Attribute | Value |
| ----- | ----- |
| VLAN | **SERVERS** |
| IP Assignment | Static (recommended) |
| Access | MGMT VLAN only |
| Data Access | Atlas only (NFS/SMB) |
| User Access | None |

---

## **🔧 Step 0 – Pre-Installation Checklist**

Before installing anything, confirm:

* Prometheus is physically connected to **Axon SERVERS VLAN port**

* Axon port is configured as **access VLAN \= SERVERS**

* SERVERS VLAN has:

  * DNS access to Cerberus

  * Internet access

  * No access from USER VLAN

* Atlas is reachable from SERVERS VLAN

* Cerberus configuration is backed up

⚠️ Do **not** proceed if Prometheus is still on USER or MGMT VLAN.

---

## **💿 Step 1 – Install Host OS**

### **Operating System**

* **Ubuntu Server LTS** (latest supported LTS)

### **Installation Settings**

* Minimal install

* No desktop environment

* OpenSSH server: **Enabled**

* Language / locale: as preferred

* Timezone: local

### **Disk Layout (Recommended)**

* OS disk only

* No data disks mounted yet

* Use default partitioning unless you have NVMe \+ separate scratch disk

---

## **🌐 Step 2 – Network Configuration**

### **Interface**

* Single NIC (initially)

* Connected to SERVERS VLAN

### **IP Configuration**

* Static IP (recommended)

  * Example:

    * IP: `192.168.X.10`

    * Gateway: `192.168.X.1`

    * DNS: `192.168.99.1` (Cerberus)

### **Validation**

From Prometheus:

* Ping Cerberus gateway

* Ping Atlas

* Resolve DNS (e.g. `ubuntu.com`)

* Reach internet (updates work)

---

## **🔐 Step 3 – Access Hardening (Baseline)**

### **User Accounts**

* Create a non-root admin user

* Disable direct root SSH login

* Use SSH keys where possible

### **SSH**

* Password auth: optional (disable later)

* SSH allowed **only from MGMT VLAN**

(Firewall enforcement handled by Cerberus)

---

## **🔄 Step 4 – System Update & Baseline Packages**

`sudo apt update`  
`sudo apt upgrade -y`  
`sudo apt install -y \`  
  `qemu-kvm \`  
  `libvirt-daemon-system \`  
  `libvirt-clients \`  
  `bridge-utils \`  
  `virt-manager \`  
  `nfs-common \`  
  `cifs-utils \`  
  `htop \`  
  `tmux \`  
  `curl \`  
  `git`

### **Enable libvirt**

`sudo systemctl enable libvirtd`  
`sudo systemctl start libvirtd`

### **Add user to libvirt group**

`sudo usermod -aG libvirt $USER`  
`newgrp libvirt`

---

## **🧠 Step 5 – Virtualization Baseline Configuration**

### **Verify KVM**

`kvm-ok`

Expected: hardware virtualization supported.

### **Set CPU Mode**

* Use **host-passthrough** for all future VMs

* Disable CPU overcommit globally

(Exact tuning documented later per VM)

---

## **📦 Step 6 – Storage Integration (Read-Only for Now)**

At this stage:

* **Do NOT create VM disks yet**

* **Do NOT copy scan data locally**

Only verify connectivity.

### **Test Atlas Access**

* Mount Atlas shares temporarily:

  * NFS (preferred) or SMB

* Confirm read/write access

* Unmount after test

This confirms Prometheus can process data *without owning it*.

---

## **🚫 Explicitly Deferred (Do NOT Do Yet)**

* ❌ Create Windows VM

* ❌ Enable GPU passthrough

* ❌ Mount permanent scan directories

* ❌ Install scanning software

* ❌ Install Docker workloads

These are **phase 2 tasks**.

---

## **🧪 Step 7 – Validation Checklist**

Prometheus is considered **initialized** when:

* OS fully updated

* Static IP set

* DNS works

* Internet access confirmed

* SSH access restricted to MGMT

* libvirt operational

* Atlas reachable

* No user VLAN access

---

## **🛑 Stopping Point (Documented)**

**Status:**  
 ✅ Prometheus initialized  
 ✅ Virtualization stack installed  
 ✅ Network correctly segmented  
 ❌ No workloads deployed

This is the **safe checkpoint** before introducing:

* Windows VM

* GPU passthrough

* 3D scanning workloads

* AI services

---

## **📌 Next Sections (Planned)**

* Prometheus Phase 2: Windows VM for MetroX

* Prometheus Phase 3: GPU passthrough

* Prometheus Phase 4: AI / container workloads

* Backup & monitoring strategy

## **Prometheus – Initialization Plan (v1.0)**

### **Role**

Prometheus is the **compute and application host** for the homelab.

Responsibilities:

* Docker containers

* Virtual machines

* AI workloads

* 3D scan processing

* Media services

* Nextcloud application

---

### **Storage Layout**

| Device | Purpose | Backup |
| ----- | ----- | ----- |
| 500 GB SSD | OS (`/`) | Yes |
| 3 × 1 TB SSD | VM / Docker storage | Yes |
| 4 TB NVMe | AI models & cache | No (disposable) |

---

### **Disposable vs Backed-Up Data**

**Disposable:**

* AI models

* Embeddings

* Checkpoints

* Temporary processing data

**Backed up:**

* VM configs

* Docker compose files

* Databases

* App configuration

Backups target **Atlas**, not Prometheus.

---

### **OS Notes**

* OS: Ubuntu Server LTS

* Do **not** use Ubuntu’s Snap-installed Nextcloud

* Application stack will be deployed via Docker

---

## **🚫 Nextcloud Installation Policy**

### **Disallowed**

* Ubuntu installer “Nextcloud” option

* Snap-based Nextcloud deployments

### **Approved**

* Dockerized Nextcloud on Prometheus

* External database (Postgres)

* Redis for file locking

* Data directory mounted from Atlas via NFS

# 3D Scanning Services

# **🧩 3D Scanning Services – Prometheus (Revopoint MetroX)**

This section documents the **authoritative architecture, roles, and procedures** for performing 3D scanning using the **Revopoint MetroX**, with processing hosted on **Prometheus**, storage on **Atlas**, and capture performed via **Nomad**.

This design intentionally avoids workstation upgrades, USB passthrough instability, and thermal/memory limitations.

---

## **🎯 Design Goals**

* Reliable scan capture

* Repeatable, high-quality processing

* Centralized compute and storage

* Minimal failure during fusion and texturing

* No changes to existing security model

---

## **🧠 Hardware Constraints & Reality Check**

### **Ares**

* Daily workstation

* Does **not** meet MetroX processing requirements

* Upgrading would be:

  * Single-purpose

  * Rarely used

  * Redundant with Prometheus

**Decision:** ❌ Not used for 3D scanning

---

### **Nomad (HP Firefly 14 G8 – Windows 11\)**

* Portable system used near the scanner

* NVIDIA GPU, but:

  * 16 GB RAM (soldered)

  * Mobile thermals

* Suitable for capture, not heavy processing

**Decision:** ✅ Capture & control only

---

### **Prometheus**

* High core-count CPU

* Large RAM capacity

* GPU-capable

* Intended for heavy compute workloads

**Decision:** ✅ Centralized 3D scan processing node

---

### **Atlas**

* NAS with parity protection

* Always-on

* Centralized access

**Decision:** ✅ Authoritative scan storage

---

## **🧱 System Roles (Authoritative)**

### **Nomad – Capture Client**

**VLAN:** USER  
 **OS:** Windows 11

**Responsibilities:**

* Connect MetroX scanner via USB

* Run Revopoint *Revo Scan*

* Perform live scanning

* Perform *light* alignment if required

* Upload raw scan projects to Atlas

**Constraints:**

* Not used for fusion, meshing, or texturing

* Avoid long processing runs

---

### **Atlas – Storage**

**VLAN:** SERVERS

**Responsibilities:**

* Store raw scan data

* Store processed meshes and exports

* Maintain backups and parity protection

**Authoritative directory structure:**

`/scans`

  `/metrox`

    `/raw`

    `/aligned`

    `/meshed`

    `/textured`

    `/exports`

---

### **Prometheus – Processing**

**VLAN:** SERVERS

**Responsibilities:**

* Host virtualization platform

* Run Windows VM for MetroX processing

* Perform:

  * Alignment

  * Fusion

  * Meshing

  * Texturing

* Write outputs back to Atlas

Prometheus **does not own data** — it processes data stored on Atlas.

---

## **🔁 Authoritative Data Flow**

`MetroX Scanner`

      `│`

      `│ USB`

      `▼`

`Nomad (Win11, USER VLAN)`

      `│`

      `│ SMB Upload`

      `▼`

`Atlas (SERVERS VLAN)`

      `│`

      `│ NFS / SMB Mount`

      `▼`

`Prometheus (SERVERS VLAN)`

      `│`

      `│ Processed Output`

      `▼`

`Atlas → Nomad (Review / Export)`

This flow avoids:

* USB passthrough complexity

* Remote desktop latency during capture

* Thermal throttling on Nomad

* Rework later

---

## **🖥 Processing Platform Decision (Locked)**

### **Host OS**

* **Ubuntu Server (LTS)** on Prometheus

### **Guest OS**

* **Windows 11 VM**

* Dedicated to MetroX processing

### **Why this model**

* Revo Scan is Windows-first

* Avoids Wine instability

* Avoids USB passthrough failures

* Predictable CPU and RAM allocation

* Clean separation of capture vs processing

---

## **⚙️ Windows VM Configuration (Recommended)**

### **Minimum (Works)**

* vCPU: 8 cores

* RAM: 32 GB

* Disk: NVMe-backed virtual disk

### **Recommended (Stable & Fast)**

* vCPU: **12–16 cores**

* RAM: **48–64 GB**

* OS Disk: 80–120 GB (NVMe-backed)

* Working data: Mounted from Atlas

* GPU: Optional (add later if needed)

### **Critical Hypervisor Settings**

* CPU mode: **host-passthrough**

* CPU pinning: **enabled**

* Memory ballooning: **disabled**

* RAM overcommit: **disabled**

⚠️ MetroX meshing and texturing can fail silently if RAM is constrained.

---

## **🗂 Storage Strategy (Critical)**

### **Rules**

* Raw scans are uploaded to Atlas

* Prometheus accesses scans via:

  * **NFS (preferred)** or

  * SMB (acceptable)

* Large scan projects **must not** live permanently inside VM disks

### **Why**

* Prevents VM disk bloat

* Makes backups automatic

* Enables easy reprocessing

* Preserves data integrity

---

## **🛠 Operational Procedure**

### **Step 1: Capture (Nomad)**

1. Connect MetroX scanner via USB

2. Run Revo Scan

3. Perform live scan

4. Save project locally

5. Avoid full fusion on Nomad

---

### **Step 2: Upload (Atlas)**

1. Connect Nomad to USER VLAN

Upload project to:

 `\\atlas\scans\metrox\raw\YYYY-MM-DD_projectname`

2.   
3. Confirm upload integrity

---

### **Step 3: Process (Prometheus)**

1. Access scan data via mounted Atlas share

2. Run alignment

3. Run fusion (monitor RAM usage)

4. Perform meshing and texturing

Export results to:

 `/scans/metrox/exports`

5. 

---

### **Step 4: Review**

* Nomad retrieves final exports from Atlas

* Files ready for CAD, printing, or archiving

---

## **🔐 Network & Security Alignment**

* Nomad → USER VLAN

* Prometheus → SERVERS VLAN

* Atlas → SERVERS VLAN

**Firewall posture:**

* USER → Atlas: ✅ SMB allowed

* Prometheus ↔ Atlas: ✅ NFS / SMB

* USER → Prometheus: ❌ blocked

* Admin access: MGMT VLAN only

No security compromises were made to support scanning.

---

## **🚫 Explicit Non-Goals**

* ❌ USB passthrough of scanner to Prometheus

* ❌ Revo Scan via Wine

* ❌ Dockerized scanning software

* ❌ Upgrading Ares

---

## **✅ Final Architecture Decision**

| System | Role |
| ----- | ----- |
| **Nomad** | Capture & control |
| **Atlas** | Authoritative storage |
| **Prometheus** | Heavy processing |
| **Ares** | Not involved |

This architecture matches how MetroX actually behaves under load and preserves your clean homelab design.

---

## **🛑 Stopping Point**

**Status:**

* Architecture finalized

* Hardware roles locked

* No upgrades required

* Awaiting Prometheus build

Safe to pause here.

# Tab 2

# **Updated To-Do (Relevant Items Only)**

### **Atlas**

* Resolve NVMe cache formatting issue

* Finalize SMB permissions

* Enable and test NFS exports

* Document share structure

### **Prometheus**

* OS installed on SSD

* Remove / ignore Snap Nextcloud

* Prepare Docker environment

* Mount Atlas NFS shares

* Define backup targets

### **Network**

* SERVERS VLAN created

* Atlas & Prometheus moved to SERVERS VLAN

* Document firewall rules per VLAN

* Restore MGMT-only admin access expectations

# Tab 10

📊 Data Strategy – Authoritative Design  
Purpose  
This section defines where data lives, what is backed up, what is disposable, and how data moves between systems.  
This strategy is designed to support:  
On-prem operation  
Temporary cloud migration  
Disaster recovery  
Compute rebuilds without data loss  
This is an authoritative declaration.  
1\. Data Classification Model  
All data in the homelab is classified into one of three categories:  
1.1 Authoritative (Persistent) Data  
Must survive any failure or rebuild  
Examples:  
Family documents  
Media libraries  
Photos  
Backups  
Application data (Nextcloud, Jellyfin config)  
Raw & processed 3D scans  
Location:  
➡️ Atlas (NAS)  
Protection:  
Parity  
Snapshots (future)  
Backup (future offsite)  
1.2 Runtime / Config State  
Important, but rebuildable if backed up  
Examples:  
Container configs  
Application databases  
Service metadata  
Location:  
Stored on Atlas  
Mounted into containers/VMs running on Prometheus or Atlas  
Rule:  
No service may store its only copy of config on a compute node.  
1.3 Disposable / Ephemeral Data  
Safe to lose  
Examples:  
AI model caches  
Temporary transcoding buffers  
Scratch datasets  
VM temp disks  
Location:  
Local disks on Prometheus  
NVMe scratch storage  
Rule:  
Disposable data is never backed up.  
2\. Storage Authority Declaration  
Atlas (Authoritative Storage)  
Atlas is the single source of truth for all persistent data.  
Atlas stores:  
Media  
Documents  
Backups  
Application data  
Scan data  
Atlas does not store:  
VM OS disks  
AI model caches  
Compute scratch space  
Atlas failures must never result in silent data loss.  
Prometheus (Compute)  
Prometheus is a disposable compute node.  
Prometheus may:  
Process data  
Cache data  
Generate outputs  
Prometheus must never be the only location of important data.  
3\. Protocol Strategy  
3.1 SMB – Human Access  
Used by:  
Nomad  
Ares  
Family devices  
Shares exposed via SMB:  
documents  
media  
photos  
backups  
scans  
Characteristics:  
User-based auth  
Familiar UX  
Mapped drives  
3.2 NFS – Compute Access  
Used by:  
Prometheus  
Linux VMs  
Containers  
Exports (planned):  
/exports/media  
/exports/appdata  
/exports/scans  
Characteristics:  
High throughput  
POSIX permissions  
Stable mounts  
4\. Backup & Portability Strategy (Defined, Not Yet Implemented)  
Backup Targets (Future)  
External disk  
Cloud object storage  
Encrypted archive  
Backup Scope  
All authoritative data on Atlas  
Selected application config directories  
Cloud Portability  
Because:  
Config is externalized  
Compute is disposable  
Data is centralized  
➡️ Services can be redeployed in cloud by restoring Atlas data to cloud storage and pointing containers at it.  
5\. Disposable vs Backed-Up (Explicit Table)  
Data Type  
Location  
Backed Up  
Media  
Atlas  
✅  
Documents  
Atlas  
✅  
Jellyfin config  
Atlas  
✅  
Nextcloud data  
Atlas  
✅  
3D scans  
Atlas  
✅  
AI models  
Prometheus NVMe  
❌  
VM OS disks  
Prometheus  
❌  
Transcode cache  
Prometheus  
❌  
6\. Documentation Stopping Point – Data Strategy  
✅ Data roles defined  
✅ Authority established  
✅ Backup scope declared  
✅ Cloud portability supported