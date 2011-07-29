var tas = {"propertiesFields": [{"typeInvite": "Enter a title", "type": "string", "name": "name", "label": "Title"}, {"type": "text", "name": "description", "cols": 30, "label": "Description"}], "modules": [{"container": {"width": 120, "terminals": [{"direction": [1, 0], "multiple": true, "name": "output", "required": false, "alwaysSrc": true, "ddConfig": {"type": "data1d.tas:out", "allowedTypes": ["data1d.tas:in"]}, "offsetPosition": {"top": 1, "right": -16}}], "xtype": "WireIt.Container", "height": 16}, "name": "Load"}, {"container": {"width": 120, "terminals": [{"direction": [-1, 0], "multiple": false, "name": "input", "required": true, "alwaysSrc": false, "ddConfig": {"type": "data1d.tas:in", "allowedTypes": ["data1d.tas:out"]}, "offsetPosition": {"top": 1, "left": -16}}], "xtype": "WireIt.Container", "height": 16}, "name": "Save"}, {"container": {"terminals": [{"direction": [-1, 0], "multiple": true, "name": "input", "required": false, "alwaysSrc": false, "ddConfig": {"type": "data1d.tas:in", "allowedTypes": ["data1d.tas:out"]}, "offsetPosition": {"top": 16, "left": -12}}, {"direction": [1, 0], "multiple": true, "name": "output", "required": false, "alwaysSrc": true, "ddConfig": {"type": "data1d.tas:out", "allowedTypes": ["data1d.tas:in"]}, "offsetPosition": {"top": 16, "left": 48}}], "xtype": "WireIt.ImageContainer", "image": "../../static/img/TAS/join.png", "icon": "../../static/img/TAS/join.png"}, "name": "Join"}, {"container": {"terminals": [{"direction": [-1, 0], "multiple": true, "name": "input", "required": false, "alwaysSrc": false, "ddConfig": {"type": "data1d.tas:in", "allowedTypes": ["data1d.tas:out"]}, "offsetPosition": {"top": 10, "left": 0}}, {"direction": [1, 0], "multiple": true, "name": "output", "required": false, "alwaysSrc": true, "ddConfig": {"type": "data1d.tas:out", "allowedTypes": ["data1d.tas:in"]}, "offsetPosition": {"top": 10, "left": 20}}], "xtype": "WireIt.ImageContainer", "image": "../../static/img/scale.png", "icon": "../../static/img/scale.png"}, "name": "Scale"}, {"container": {"terminals": [{"direction": [-1, 0], "multiple": false, "name": "input", "required": false, "alwaysSrc": false, "ddConfig": {"type": "data1d.tas:in", "allowedTypes": ["data1d.tas:out"]}, "offsetPosition": {"top": 16, "left": -12}}, {"direction": [1, 0], "multiple": true, "name": "output", "required": false, "alwaysSrc": true, "ddConfig": {"type": "data1d.tas:out", "allowedTypes": ["data1d.tas:in"]}, "offsetPosition": {"top": 16, "left": 48}}], "xtype": "WireIt.ImageContainer", "image": "../../static/img/TAS/monitor_normalization.png", "icon": "../../static/img/TAS/monitor_normalization.png"}, "name": "Normalize Monitor"}, {"container": {"terminals": [{"direction": [-1, 0], "multiple": false, "name": "input", "required": false, "alwaysSrc": false, "ddConfig": {"type": "data1d.tas:in", "allowedTypes": ["data1d.tas:out"]}, "offsetPosition": {"top": 16, "left": -12}}, {"direction": [1, 0], "multiple": true, "name": "output", "required": false, "alwaysSrc": true, "ddConfig": {"type": "data1d.tas:out", "allowedTypes": ["data1d.tas:in"]}, "offsetPosition": {"top": 16, "left": 48}}], "xtype": "WireIt.ImageContainer", "image": "../../static/img/TAS/detailed_balance.png", "icon": "../../static/img/TAS/detailed_balance.png"}, "name": "Detailed Balance"}, {"container": {"terminals": [{"direction": [-1, 0], "multiple": false, "name": "input", "required": false, "alwaysSrc": false, "ddConfig": {"type": "data1d.tas:in", "allowedTypes": ["data1d.tas:out"]}, "offsetPosition": {"top": 16, "left": -12}}, {"direction": [1, 0], "multiple": true, "name": "output", "required": false, "alwaysSrc": true, "ddConfig": {"type": "data1d.tas:out", "allowedTypes": ["data1d.tas:in"]}, "offsetPosition": {"top": 16, "left": 48}}], "xtype": "WireIt.ImageContainer", "image": "../../static/img/TAS/harmonic_monitor_correction.png", "icon": "../../static/img/TAS/harmonic_monitor_correction.png"}, "name": "Monitor Correction"}, {"container": {"terminals": [{"direction": [-1, 0], "multiple": false, "name": "input", "required": false, "alwaysSrc": false, "ddConfig": {"type": "data1d.tas:in", "allowedTypes": ["data1d.tas:out"]}, "offsetPosition": {"top": 16, "left": -12}}, {"direction": [1, 0], "multiple": true, "name": "output", "required": false, "alwaysSrc": true, "ddConfig": {"type": "data1d.tas:out", "allowedTypes": ["data1d.tas:in"]}, "offsetPosition": {"top": 16, "left": 48}}], "xtype": "WireIt.ImageContainer", "image": "../../static/img/TAS/volume_resolution_correction.png", "icon": "../../static/img/TAS/volume_resolution_correction.png"}, "name": "Volume Correction"}], "languageName": "NCNR BT7"}

