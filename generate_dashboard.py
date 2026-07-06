import json

dashboard = {
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": {
          "type": "grafana",
          "uid": "-- Grafana --"
        },
        "enable": True,
        "hide": True,
        "iconColor": "rgba(0, 211, 255, 1)",
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
  "tags": ["shelly", "power"],
  "templating": {
    "list": []
  },
  "time": {"from": "now-6h", "to": "now"},
  "timepicker": {},
  "timezone": "browser",
  "title": "Shelly Energy Monitoring (InfluxDB v3 Fixed)",
  "uid": "shelly-energy-06",
  "version": 1
}

def make_sql_target(select_clause, alias, ref_id="A"):
    # Using SQL for official InfluxDB plugin (v3)
    sql_query = f"""
SELECT 
  time,
  {select_clause} AS "{alias}"
FROM "shelly_metrics"
WHERE 
  $__timeFilter(time)
ORDER BY time ASC
    """.strip()
    
    return {
      "alias": alias,
      "datasource": {
        "type": "influxdb",
        "uid": "${DS_INFLUXDB}"
      },
      "query": sql_query,
      "rawSql": sql_query,
      "queryText": sql_query,
      "rawQuery": True,
      "refId": ref_id,
      "format": "time_series"
    }

def make_diff_target(field, alias, ref_id="A"):
    # Calculates the difference between the maximum and minimum value in the selected time range
    sql_query = f"""
SELECT 
  MAX(time) AS time,
  MAX("{field}") - MIN("{field}") AS "{alias}"
FROM "shelly_metrics"
WHERE 
  $__timeFilter(time)
    """.strip()
    
    return {
      "alias": alias,
      "datasource": {
        "type": "influxdb",
        "uid": "${DS_INFLUXDB}"
      },
      "query": sql_query,
      "rawSql": sql_query,
      "queryText": sql_query,
      "rawQuery": True,
      "refId": ref_id,
      "format": "table"  # Returning table format since it's a single aggregate row, not a timeseries
    }

# Panel 1: Current Power (Stat)
panel_power_stat = {
  "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "thresholds"},
      "mappings": [],
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"color": "green", "value": None},
          {"color": "orange", "value": 1000},
          {"color": "red", "value": 2000}
        ]
      },
      "unit": "watt"
    },
    "overrides": []
  },
  "gridPos": {"h": 6, "w": 6, "x": 0, "y": 0},
  "id": 1,
  "options": {
    "colorMode": "value",
    "graphMode": "area",
    "justifyMode": "auto",
    "orientation": "auto",
    "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
    "textMode": "auto"
  },
  "targets": [make_sql_target('"power_w"', "Power")],
  "title": "Current Power",
  "type": "stat"
}

# Panel 2: Total Energy (Stat)
panel_energy_stat = {
  "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "thresholds"},
      "mappings": [],
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"color": "blue", "value": None}
        ]
      },
      "unit": "watth"
    },
    "overrides": []
  },
  "gridPos": {"h": 6, "w": 6, "x": 6, "y": 0},
  "id": 2,
  "options": {
    "colorMode": "none",
    "graphMode": "none",
    "justifyMode": "auto",
    "orientation": "auto",
    "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
    "textMode": "auto"
  },
  # Use the new target that calculates MAX - MIN
  "targets": [make_diff_target('energy_total_wh', "Energy")],
  "title": "Energy Consumed (Selected Range)",
  "type": "stat"
}

# Panel 3: Voltage (Gauge)
panel_voltage_gauge = {
  "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "thresholds"},
      "mappings": [],
      "min": 200,
      "max": 260,
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"color": "red", "value": None},
          {"color": "green", "value": 220},
          {"color": "red", "value": 250}
        ]
      },
      "unit": "volt"
    },
    "overrides": []
  },
  "gridPos": {"h": 6, "w": 6, "x": 12, "y": 0},
  "id": 3,
  "options": {
    "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
    "showThresholdLabels": False,
    "showThresholdMarkers": True
  },
  "targets": [make_sql_target('"voltage_v"', "Voltage")],
  "title": "Voltage",
  "type": "gauge"
}

# Panel 4: Temperature (Gauge)
panel_temp_gauge = {
  "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "thresholds"},
      "mappings": [],
      "min": 20,
      "max": 100,
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"color": "green", "value": None},
          {"color": "orange", "value": 60},
          {"color": "red", "value": 80}
        ]
      },
      "unit": "celsius"
    },
    "overrides": []
  },
  "gridPos": {"h": 6, "w": 6, "x": 18, "y": 0},
  "id": 4,
  "options": {
    "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
    "showThresholdLabels": False,
    "showThresholdMarkers": True
  },
  "targets": [make_sql_target('"temperature_c"', "Temp")],
  "title": "Device Temperature",
  "type": "gauge"
}

# Panel 5: Power Time Series
panel_power_ts = {
  "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "palette-classic"},
      "custom": {
        "axisPlacement": "auto",
        "drawStyle": "line",
        "fillOpacity": 20,
        "gradientMode": "opacity",
        "lineInterpolation": "smooth",
        "lineWidth": 2,
        "showPoints": "never"
      },
      "mappings": [],
      "unit": "watt"
    },
    "overrides": []
  },
  "gridPos": {"h": 9, "w": 24, "x": 0, "y": 6},
  "id": 5,
  "options": {
    "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True},
    "tooltip": {"mode": "multi"}
  },
  "targets": [make_sql_target('"power_w"', "Power")],
  "title": "Power Consumption over Time",
  "type": "timeseries"
}

# Panel 6: Current and Voltage Time Series (Dual Axis)
panel_current_voltage_ts = {
  "datasource": {"type": "influxdb", "uid": "${DS_INFLUXDB}"},
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "palette-classic"},
      "custom": {
        "axisPlacement": "auto",
        "drawStyle": "line",
        "fillOpacity": 10,
        "gradientMode": "none",
        "lineInterpolation": "linear",
        "lineWidth": 1,
        "showPoints": "never"
      },
      "mappings": []
    },
    "overrides": [
      {
        "matcher": {"id": "byName", "options": "Current"},
        "properties": [
          {"id": "unit", "value": "amp"},
          {"id": "custom.axisPlacement", "value": "left"}
        ]
      },
      {
        "matcher": {"id": "byName", "options": "Voltage"},
        "properties": [
          {"id": "unit", "value": "volt"},
          {"id": "custom.axisPlacement", "value": "right"}
        ]
      }
    ]
  },
  "gridPos": {"h": 9, "w": 24, "x": 0, "y": 15},
  "id": 6,
  "options": {
    "legend": {"displayMode": "list", "placement": "bottom", "showLegend": True},
    "tooltip": {"mode": "multi"}
  },
  "targets": [
    make_sql_target('"current_a"', "Current", "A"),
    make_sql_target('"voltage_v"', "Voltage", "B")
  ],
  "title": "Current vs Voltage",
  "type": "timeseries"
}

dashboard["panels"] = [
    panel_power_stat,
    panel_energy_stat,
    panel_voltage_gauge,
    panel_temp_gauge,
    panel_power_ts,
    panel_current_voltage_ts
]

dashboard["__inputs"] = [
  {
    "name": "DS_INFLUXDB",
    "label": "InfluxDB v3 Datasource",
    "description": "Select the InfluxDB v3 (SQL) datasource for Shelly metrics",
    "type": "datasource",
    "pluginId": "influxdb"
  }
]

with open('shelly_dashboard.json', 'w') as f:
    json.dump(dashboard, f, indent=2)

print("Updated shelly_dashboard.json to calculate energy difference.")
