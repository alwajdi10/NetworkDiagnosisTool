# NetDiagnostics - Network Troubleshooting Tool
NetDiagnostix  is a powerful and intuitive network diagnostic and troubleshooting tool developed as a Summer internship project. It is designed to help network administrators and IT professionals quickly identify, analyze, and resolve network issues through a suite of integrated utilities.

# ✨ Features
NetDiagnostix provides a comprehensive set of tools to give you deep insights into your network's health and performance:

# 📍 Connectivity Analysis:
Quickly verify the availability and responsiveness of devices (servers, printers, IoT devices) on your network using ICMP ping and custom TCP port checks.

# 🚀 Performance Testing:
Measure key performance metrics to identify bottlenecks.

# Latency & Jitter: 
Determine the delay in communication for real-time applications like VoIP and gaming.

# Bandwidth Estimation:
Get an estimate of the available bandwidth between points.

# Response Time:
Track the time it takes for a device to respond to a request.

🗺️ Network Mapping: Automatically discover devices on the local network and visualize the network topology, helping you understand how devices are interconnected.

📈 Real-Time Monitoring: Continuously monitor the status of critical network devices and services. Receive instant visual alerts and notifications for downtime or performance degradation.

📊 Reports and History: Generate detailed, exportable reports (PDF, CSV) on network performance trends and past incidents for analysis and compliance.

# 🛠️ Tech Stack
Language: Python 3.x

Key Libraries:

scapy / socket for low-level network packet manipulation and discovery.

ping3 / python-ping for ICMP-based connectivity and latency checks.

speedtest-cli or custom TCP sockets for bandwidth testing.

psutil for system and network monitoring.

tkinter / PyQt5 / CustomTkinter for the graphical user interface (GUI).

matplotlib / seaborn for data visualization and graph generation in reports.

reportlab / pandas for generating PDF/CSV reports.

Concept: OSI Layers 2 (Data Link) and 3 (Network).

# 📦 Installation
Clone the repository:

bash
git clone https://github.com/alwajdi10/NetworkDiagnosisTool
cd net-diagnostix-tool
(Recommended) Create a virtual environment:

bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
Install the required dependencies:

bash
pip install -r requirements.txt
🚀 Usage
After installation and activating your virtual environment, you can run the application:

bash
python main.py
# Basic Workflow:

Launch the application. The main dashboard will show an overview of your network interface.

Use the Discovery tab to scan your network and map connected devices.

Select a device from the map or list to run specific tests (Ping, Traceroute, Bandwidth).

Navigate to the Monitor tab to add critical devices to the real-time watchlist.

View all historical data and generate reports from the Reports section.

 #  📷 Screenshots
<img width="1877" height="907" alt="image" src="https://github.com/user-attachments/assets/6a56be71-5a68-41bc-a201-7c71d082abba" />
<img width="1510" height="476" alt="image" src="https://github.com/user-attachments/assets/48d211d8-5398-4f76-8ec8-d8dea00e872c" />
<img width="1509" height="379" alt="image" src="https://github.com/user-attachments/assets/d4cddce4-8b02-4794-ae4d-3393aaf078b6" />
<img width="744" height="914" alt="image" src="https://github.com/user-attachments/assets/3b8711fb-04cf-4e8a-95c2-027411a7d8ee" />

# 🙏 Acknowledgments
This project was developed as part of a Summer internship.

Thanks to My tutors for thier guidance throughout this journey.

