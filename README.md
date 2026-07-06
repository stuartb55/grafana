# Grafana Dashboards Repository

This repository contains exported Grafana dashboard templates and generation scripts designed to monitor various smart home and IoT systems. Many of these dashboards are specifically tailored to query **InfluxDB v3** (using native SQL via the official InfluxDB Grafana plugin).

## Dashboards Included

### 1. Frigate NVR Monitoring (`frigate_dashboard.json`)
A comprehensive and creative dashboard to monitor the health and performance of your Frigate Network Video Recorder.
- **Key Metrics**: Total System FPS, Detector Inference Speed, Camera & Detection FPS breakdowns.
- **Diagnostics**: Deep dive into CPU usage separated by process (`ffmpeg`, `capture`, `detect`) to help optimize hardware acceleration.
- **Audio Levels**: Real-time equalizer-style bar gauges for live `audio_dbfs` and historical `audio_rms` trends.
- **Stream Health**: Alerts and tracking for dropped frames (`skipped_fps`) and stream stalls (`stalls_hour`).

### 2. Shelly Smart Plug Energy (`shelly_dashboard.json`)
Monitors telemetry and energy usage from Shelly smart devices (e.g., Shelly 1PM Gen4).
- **Key Metrics**: Real-time Power Consumption (Watts), Total Energy Consumed in selected window (kWh).
- **Sensors**: Device Temperature, supply Voltage, Wi-Fi Signal Strength (RSSI).
- **Design**: Dual-axis overlays comparing Current draw vs Voltage sags.

### 3. Ruuvi Sensors (`ruuvi.json`)
Monitors telemetry from Ruuvi Bluetooth environmental sensors (Temperature, Humidity, etc.) queried via Prometheus.

### 4. Legacy Frigate (`frigate.json`)
An alternate/legacy dashboard for Frigate NVR.

---

## How to Import

1. Open your Grafana instance in your web browser.
2. Navigate to **Dashboards** > **New** > **Import**.
3. Click **Upload JSON file** and select the desired `.json` file from this repository.
4. When prompted, map the dashboard to your corresponding configured Datasource (e.g., your InfluxDB v3 connection).
5. Click **Import**.

## Developer Tools

If you need to make structural changes to the dashboards, they can be regenerated using the included Python scripts:
- `generate_dashboard.py` (Rebuilds the Shelly dashboard)
- `generate_frigate_dashboard.py` (Rebuilds the Frigate dashboard)

*Note: These scripts automatically format InfluxDB v3 SQL queries properly and inject necessary Grafana transformations (like `partitionByValues`) so Grafana correctly splits series lines.*
