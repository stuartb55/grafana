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
  "tags": ["frigate", "nvr"],
  "templating": {"list": []},
  "time": {"from": "now-3h", "to": "now"},
  "timepicker": {},
  "timezone": "browser",
  "title": "Frigate NVR Advanced Metrics",
  "uid": "frigate-advanced-01",
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
      "format": "table"  # Returning as table and letting transformations handle time-series splitting
    }

# Common transformation to split by a tag (like 'camera' or 'detector') to ensure lines render
def partition_by(field):
    return [
        {
            "id": "partitionByValues",
            "options": {"fields": [field]}
        }
    ]

# Row 1: System Health
panel_uptime = {
  "datasource": {"uid": "${DS_INFLUXDB}"},
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "palette-classic"},
      "mappings": [],
      "unit": "s" # uptime is in seconds
    }
  },
  "gridPos": {"h": 5, "w": 4, "x": 0, "y": 0},
  "id": 1,
  "options": {
    "colorMode": "none",
    "graphMode": "none",
    "reduceOptions": {"calcs": ["lastNotNull"]},
    "textMode": "auto"
  },
  "targets": [make_sql_target('"uptime"', "frigate_system", "A")],
  "title": "System Uptime",
  "type": "stat"
}

panel_stalls = {
  "datasource": {"uid": "${DS_INFLUXDB}"},
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "thresholds"},
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"color": "green", "value": None},
          {"color": "orange", "value": 1},
          {"color": "red", "value": 5}
        ]
      }
    }
  },
  "gridPos": {"h": 5, "w": 4, "x": 4, "y": 0},
  "id": 2,
  "options": {
    "colorMode": "value",
    "graphMode": "none",
    "reduceOptions": {"calcs": ["sum"]}
  },
  "targets": [make_sql_target('"stalls_hour"', "frigate_camera", "A")],
  "title": "Total Stalls (Selected Range)",
  "type": "stat"
}

panel_skipped_fps = {
  "datasource": {"uid": "${DS_INFLUXDB}"},
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "thresholds"},
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"color": "green", "value": None},
          {"color": "orange", "value": 1},
          {"color": "red", "value": 5}
        ]
      },
      "unit": "fps"
    }
  },
  "gridPos": {"h": 5, "w": 4, "x": 8, "y": 0},
  "id": 3,
  "options": {
    "colorMode": "value",
    "graphMode": "area",
    "reduceOptions": {"calcs": ["mean"]}
  },
  "targets": [make_sql_target('"skipped_fps"', "frigate_camera", "A")],
  "title": "Avg Skipped FPS",
  "type": "stat"
}

panel_inference = {
  "datasource": {"uid": "${DS_INFLUXDB}"},
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "thresholds"},
      "min": 0,
      "max": 50,
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"color": "green", "value": None},
          {"color": "orange", "value": 15},
          {"color": "red", "value": 30}
        ]
      },
      "unit": "ms"
    }
  },
  "gridPos": {"h": 5, "w": 12, "x": 12, "y": 0},
  "id": 4,
  "options": {
    "reduceOptions": {"calcs": ["lastNotNull"]},
    "showThresholdLabels": False,
    "showThresholdMarkers": True
  },
  "targets": [make_sql_target('"inference_speed", "detector"', "frigate_detector", "A")],
  "transformations": partition_by("detector"),
  "title": "Current Inference Speed",
  "type": "gauge"
}

# Row 2: Deep Dive Timeseries (FPS breakdown)
panel_fps_breakdown = {
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
      "unit": "fps"
    }
  },
  "gridPos": {"h": 8, "w": 12, "x": 0, "y": 5},
  "id": 5,
  "options": {
    "legend": {"displayMode": "table", "placement": "bottom"}
  },
  "targets": [
    make_sql_target('"camera_fps", "camera"', "frigate_camera", "A")
  ],
  "transformations": partition_by("camera"),
  "title": "Capture FPS Stream Quality",
  "type": "timeseries"
}

panel_process_vs_detect = {
  "datasource": {"uid": "${DS_INFLUXDB}"},
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "palette-classic"},
      "custom": {
        "drawStyle": "line",
        "lineWidth": 1,
        "showPoints": "never"
      },
      "unit": "fps"
    }
  },
  "gridPos": {"h": 8, "w": 12, "x": 12, "y": 5},
  "id": 6,
  "options": {
    "legend": {"displayMode": "table", "placement": "bottom"}
  },
  "targets": [
    make_sql_target('"process_fps", "camera"', "frigate_camera", "A"),
    make_sql_target('"detection_fps", "camera"', "frigate_camera", "B")
  ],
  "transformations": partition_by("camera"),
  "title": "Processing vs Detection FPS",
  "type": "timeseries"
}

# Row 3: Audio Levels (Creative Bar Gauge)
panel_audio_levels = {
  "datasource": {"uid": "${DS_INFLUXDB}"},
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "thresholds"},
      "min": -100,
      "max": 0,
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"color": "green", "value": None},
          {"color": "orange", "value": -40},
          {"color": "red", "value": -10}
        ]
      },
      "unit": "dB" # DBFS
    }
  },
  "gridPos": {"h": 6, "w": 12, "x": 0, "y": 13},
  "id": 7,
  "options": {
    "displayMode": "gradient",
    "orientation": "horizontal",
    "reduceOptions": {"calcs": ["lastNotNull"]}
  },
  "targets": [make_sql_target('"audio_dbfs", "camera"', "frigate_camera", "A")],
  "transformations": partition_by("camera"),
  "title": "Live Audio Levels (dBFS)",
  "type": "bargauge"
}

panel_audio_rms = {
  "datasource": {"uid": "${DS_INFLUXDB}"},
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "palette-classic"},
      "custom": {
        "drawStyle": "line",
        "fillOpacity": 30,
        "lineWidth": 1,
        "showPoints": "never"
      }
    }
  },
  "gridPos": {"h": 6, "w": 12, "x": 12, "y": 13},
  "id": 8,
  "options": {
    "legend": {"displayMode": "list", "placement": "bottom"}
  },
  "targets": [make_sql_target('"audio_rms", "camera"', "frigate_camera", "A")],
  "transformations": partition_by("camera"),
  "title": "Audio RMS History",
  "type": "timeseries"
}

# Row 4: CPU Diagnostics Breakdown
panel_camera_cpu = {
  "datasource": {"uid": "${DS_INFLUXDB}"},
  "fieldConfig": {
    "defaults": {
      "color": {"mode": "palette-classic"},
      "custom": {
        "drawStyle": "line",
        "fillOpacity": 15,
        "lineWidth": 1,
        "showPoints": "never",
        "stacking": {"group": "A", "mode": "normal"} # Stack CPU utilization
      },
      "unit": "percent"
    }
  },
  "gridPos": {"h": 8, "w": 24, "x": 0, "y": 19},
  "id": 9,
  "options": {
    "legend": {"displayMode": "table", "placement": "bottom"}
  },
  "targets": [
    make_sql_target('"ffmpeg_cpu" AS "FFMPEG", "camera"', "frigate_camera", "A"),
    make_sql_target('"capture_cpu" AS "Capture", "camera"', "frigate_camera", "B"),
    make_sql_target('"detect_cpu" AS "Detect", "camera"', "frigate_camera", "C")
  ],
  "transformations": partition_by("camera"),
  "title": "Stacked CPU Usage per Camera Process",
  "type": "timeseries"
}

dashboard["panels"] = [
    panel_uptime,
    panel_stalls,
    panel_skipped_fps,
    panel_inference,
    panel_fps_breakdown,
    panel_process_vs_detect,
    panel_audio_levels,
    panel_audio_rms,
    panel_camera_cpu
]

dashboard["__inputs"] = [
  {
    "name": "DS_INFLUXDB",
    "label": "InfluxDB v3 Datasource (Frigate)",
    "description": "Select the InfluxDB v3 (SQL) datasource for Frigate metrics",
    "type": "datasource",
    "pluginId": "influxdb"
  }
]

with open('frigate_dashboard.json', 'w') as f:
    json.dump(dashboard, f, indent=2)

print("Updated frigate_dashboard.json with creative layouts and transformations.")
