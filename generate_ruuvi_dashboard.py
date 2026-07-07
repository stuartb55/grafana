import json

dashboard = {
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": {"type": "grafana", "uid": "-- Grafana --"},
        "enable": True,
        "hide": True,
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": True,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 1,
  "id": None,
  "links": [],
  "liveNow": True,
  "panels": [],
  "refresh": "10s",
  "schemaVersion": 39,
  "tags": ["ruuvi", "sensors"],
  "templating": {"list": []},
  "time": {"from": "now-6h", "to": "now"},
  "timepicker": {},
  "timezone": "browser",
  "title": "Ruuvi Sensors",
  "uid": "ruuvi-sensors-01",
  "version": 1
}

def make_sql_target(select_clause, from_table, ref_id="A"):
    sql_query = f"""
SELECT 
  time,
  {select_clause}
FROM "{from_table}"
WHERE 
  $__timeFilter(time)
ORDER BY time ASC
    """.strip()
    
    return {
      "alias": "",
      "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
      "query": sql_query,
      "rawSql": sql_query,
      "queryText": sql_query,
      "rawQuery": True,
      "refId": ref_id,
      "format": "table"
    }

def partition_by(field):
    return [
        {
            "id": "partitionByValues",
            "options": {"fields": [field]}
        }
    ]

# Gauges
def make_gauge_panel(title, select_clause, unit, x, id_num, min_val=None, max_val=None, thresholds=None):
    if thresholds is None:
        thresholds = {
            "mode": "absolute",
            "steps": [{"color": "green", "value": None}]
        }
    
    panel = {
      "datasource": {"uid": "${DS_INFLUXDB}"},
      "fieldConfig": {
        "defaults": {
          "color": {"mode": "thresholds"},
          "thresholds": thresholds,
          "unit": unit
        }
      },
      "gridPos": {"h": 6, "w": 6, "x": x, "y": 0},
      "id": id_num,
      "options": {
        "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
        "orientation": "auto",
        "showThresholdLabels": False,
        "showThresholdMarkers": True
      },
      "targets": [
        make_sql_target(select_clause, "ruuvi_measurements", "A")
      ],
      "transformations": partition_by("name"),
      "title": title,
      "type": "gauge"
    }
    
    if min_val is not None:
        panel["fieldConfig"]["defaults"]["min"] = min_val
    if max_val is not None:
        panel["fieldConfig"]["defaults"]["max"] = max_val
        
    return panel

panel_temp_gauge = make_gauge_panel("Current Temp", '"temperature", "name"', "celsius", 0, 5, -20, 60, {
    "mode": "absolute", "steps": [{"color": "blue", "value": None}, {"color": "green", "value": 15}, {"color": "red", "value": 30}]
})
panel_hum_gauge = make_gauge_panel("Current Humidity", '"humidity", "name"', "percent", 6, 6, 0, 100, {
    "mode": "absolute", "steps": [{"color": "orange", "value": None}, {"color": "green", "value": 30}, {"color": "blue", "value": 60}]
})
panel_pressure_gauge = make_gauge_panel("Current Pressure", '"pressure", "name"', "pressurehpa", 12, 7, 950, 1050)
panel_battery_gauge = make_gauge_panel("Current Battery", '"batteryVoltage", "name"', "volt", 18, 8, 2.0, 3.5, {
    "mode": "absolute", "steps": [{"color": "red", "value": None}, {"color": "orange", "value": 2.5}, {"color": "green", "value": 2.8}]
})

# Timeseries Helper
def make_ts_panel(title, select_clause, unit, x, y, id_num):
    return {
      "datasource": {"uid": "${DS_INFLUXDB}"},
      "fieldConfig": {
        "defaults": {
          "color": {"mode": "palette-classic"},
          "custom": {
            "drawStyle": "line",
            "fillOpacity": 10,
            "lineWidth": 2,
            "showPoints": "never"
          },
          "unit": unit
        }
      },
      "gridPos": {"h": 8, "w": 12, "x": x, "y": y},
      "id": id_num,
      "options": {
        "legend": {"displayMode": "table", "placement": "bottom"}
      },
      "targets": [
        make_sql_target(select_clause, "ruuvi_measurements", "A")
      ],
      "transformations": partition_by("name"),
      "title": title,
      "type": "timeseries"
    }

panel_temp = make_ts_panel("Temperature", '"temperature", "name"', "celsius", 0, 6, 1)
panel_hum = make_ts_panel("Humidity", '"humidity", "name"', "percent", 12, 6, 2)
panel_pressure = make_ts_panel("Pressure", '"pressure", "name"', "pressurehpa", 0, 14, 3)
panel_battery = make_ts_panel("Battery Voltage", '"batteryVoltage", "name"', "volt", 12, 14, 4)
panel_co2 = make_ts_panel("CO2", '"co2", "name"', "ppm", 0, 22, 9)
panel_voc = make_ts_panel("VOC", '"voc", "name"', "ppm", 12, 22, 10)
panel_pm2p5 = make_ts_panel("PM2.5", '"pm2p5", "name"', "µg/m3", 0, 30, 11)
panel_dew_point = make_ts_panel("Dew Point", '"dewPoint", "name"', "celsius", 12, 30, 12)
panel_abs_hum = make_ts_panel("Absolute Humidity", '"absoluteHumidity", "name"', "g/m3", 0, 38, 13)
panel_rssi = make_ts_panel("RSSI", '"rssi", "name"', "dBm", 12, 38, 14)

dashboard["panels"] = [
    panel_temp_gauge,
    panel_hum_gauge,
    panel_pressure_gauge,
    panel_battery_gauge,
    panel_temp,
    panel_hum,
    panel_pressure,
    panel_battery,
    panel_co2,
    panel_voc,
    panel_pm2p5,
    panel_dew_point,
    panel_abs_hum,
    panel_rssi
]

dashboard["__inputs"] = [
  {
    "name": "DS_INFLUXDB",
    "label": "InfluxDB v3 Datasource (Ruuvi)",
    "description": "Select the InfluxDB v3 (SQL) datasource for Ruuvi metrics",
    "type": "datasource",
    "pluginId": "influxdb"
  }
]

with open('ruuvi.json', 'w') as f:
    json.dump(dashboard, f, indent=2)

print("Updated ruuvi.json")
