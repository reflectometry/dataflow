var andrlang = {
    "modules": [
        {
            "container": {
                "width": 120, 
                "terminals": [
                    {
                        "direction": [
                            1, 
                            0
                        ], 
                        "multiple": true, 
                        "name": "output", 
                        "required": false, 
                        "alwaysSrc": true, 
                        "ddConfig": {
                            "type": "data1d.ospec:out", 
                            "allowedTypes": [
                                "data1d.ospec:in"
                            ]
                        }, 
                        "offsetPosition": {
                            "top": 1, 
                            "right": -16
                        }
                    }
                ], 
                "xtype": "WireIt.Container", 
                "height": 16
            }, 
            "name": "Load"
        }, 
        {
            "container": {
                "width": 120, 
                "terminals": [
                    {
                        "direction": [
                            -1, 
                            0
                        ], 
                        "multiple": false, 
                        "name": "input", 
                        "required": true, 
                        "alwaysSrc": false, 
                        "ddConfig": {
                            "type": "data1d.ospec:in", 
                            "allowedTypes": [
                                "data1d.ospec:out"
                            ]
                        }, 
                        "offsetPosition": {
                            "top": 1, 
                            "left": -16
                        }
                    }
                ], 
                "xtype": "WireIt.Container", 
                "height": 16
            }, 
            "name": "Save"
        }, 
        {
            "container": {
                "terminals": [
                    {
                        "direction": [
                            -1, 
                            0
                        ], 
                        "multiple": true, 
                        "name": "input", 
                        "required": false, 
                        "alwaysSrc": false, 
                        "ddConfig": {
                            "type": "data1d.ospec:in", 
                            "allowedTypes": [
                                "data1d.ospec:out"
                            ]
                        }, 
                        "offsetPosition": {
                            "top": 1, 
                            "left": -15
                        }
                    }, 
                    {
                        "direction": [
                            1, 
                            0
                        ], 
                        "multiple": true, 
                        "name": "output", 
                        "required": false, 
                        "alwaysSrc": true, 
                        "ddConfig": {
                            "type": "data1d.ospec:out", 
                            "allowedTypes": [
                                "data1d.ospec:in"
                            ]
                        }, 
                        "offsetPosition": {
                            "top": 1, 
                            "left": 15
                        }
                    }
                ], 
                "xtype": "WireIt.ImageContainer", 
                "image": "../../static/img/rowantests/grid.png", 
                "icon": "../../static/img/rowantests/grid.png"
            }, 
            "name": "Autogrid"
        }, 
        {
            "container": {
                "terminals": [
                    {
                        "direction": [
                            -1, 
                            0
                        ], 
                        "multiple": true, 
                        "name": "input", 
                        "required": false, 
                        "alwaysSrc": false, 
                        "ddConfig": {
                            "type": "data1d.ospec:in", 
                            "allowedTypes": [
                                "data1d.ospec:out"
                            ]
                        }, 
                        "offsetPosition": {
                            "top": 1, 
                            "left": -15
                        }
                    }, 
                    {
                        "direction": [
                            1, 
                            0
                        ], 
                        "multiple": true, 
                        "name": "output", 
                        "required": false, 
                        "alwaysSrc": true, 
                        "ddConfig": {
                            "type": "data1d.ospec:out", 
                            "allowedTypes": [
                                "data1d.ospec:in"
                            ]
                        }, 
                        "offsetPosition": {
                            "top": 1, 
                            "left": 15
                        }
                    }
                ], 
                "xtype": "WireIt.ImageContainer", 
                "image": "../../static/img/rowantests/sum.png", 
                "icon": "../../static/img/rowantests/sum.png"
            }, 
            "name": "Join"
        }, 
        {
            "container": {
                "terminals": [
                    {
                        "direction": [
                            -1, 
                            0
                        ], 
                        "multiple": true, 
                        "name": "input", 
                        "required": false, 
                        "alwaysSrc": false, 
                        "ddConfig": {
                            "type": "data1d.ospec:in", 
                            "allowedTypes": [
                                "data1d.ospec:out"
                            ]
                        }, 
                        "offsetPosition": {
                            "top": 10, 
                            "left": 0
                        }
                    }, 
                    {
                        "direction": [
                            1, 
                            0
                        ], 
                        "multiple": true, 
                        "name": "output", 
                        "required": false, 
                        "alwaysSrc": true, 
                        "ddConfig": {
                            "type": "data1d.ospec:out", 
                            "allowedTypes": [
                                "data1d.ospec:in"
                            ]
                        }, 
                        "offsetPosition": {
                            "top": 10, 
                            "left": 20
                        }
                    }
                ], 
                "xtype": "WireIt.ImageContainer", 
                "image": "../../static/img/rowantests/offset.png", 
                "icon": "../../static/img/rowantests/offset.png"
            }, 
            "name": "Offset"
        }, 
        {
            "container": {
                "terminals": [
                    {
                        "direction": [
                            -1, 
                            0
                        ], 
                        "multiple": true, 
                        "name": "input", 
                        "required": false, 
                        "alwaysSrc": false, 
                        "ddConfig": {
                            "type": "data1d.ospec:in", 
                            "allowedTypes": [
                                "data1d.ospec:out"
                            ]
                        }, 
                        "offsetPosition": {
                            "top": 10, 
                            "left": 0
                        }
                    }, 
                    {
                        "direction": [
                            1, 
                            0
                        ], 
                        "multiple": true, 
                        "name": "output", 
                        "required": false, 
                        "alwaysSrc": true, 
                        "ddConfig": {
                            "type": "data1d.ospec:out", 
                            "allowedTypes": [
                                "data1d.ospec:in"
                            ]
                        }, 
                        "offsetPosition": {
                            "top": 10, 
                            "left": 20
                        }
                    }
                ], 
                "xtype": "WireIt.ImageContainer", 
                "image": "../../static/img/rowantests/wiggle.png", 
                "icon": "../../static/img/rowantests/wiggle.png"
            }, 
            "name": "Wiggle"
        }, 
        {
            "container": {
                "terminals": [
                    {
                        "direction": [
                            -1, 
                            0
                        ], 
                        "multiple": true, 
                        "name": "input", 
                        "required": false, 
                        "alwaysSrc": false, 
                        "ddConfig": {
                            "type": "data1d.ospec:in", 
                            "allowedTypes": [
                                "data1d.ospec:out"
                            ]
                        }, 
                        "offsetPosition": {
                            "top": 10, 
                            "left": 0
                        }
                    }, 
                    {
                        "direction": [
                            1, 
                            0
                        ], 
                        "multiple": true, 
                        "name": "output", 
                        "required": false, 
                        "alwaysSrc": true, 
                        "ddConfig": {
                            "type": "data1d.ospec:out", 
                            "allowedTypes": [
                                "data1d.ospec:in"
                            ]
                        }, 
                        "offsetPosition": {
                            "top": 10, 
                            "left": 20
                        }
                    }
                ], 
                "xtype": "WireIt.ImageContainer", 
                "image": "../../static/img/rowantests/twotheta.png", 
                "icon": "../../static/img/rowantests/twotheta.png"
            }, 
            "name": "Pixels to two theta"
        }, 
        {
            "container": {
                "terminals": [
                    {
                        "direction": [
                            -1, 
                            0
                        ], 
                        "multiple": true, 
                        "name": "input", 
                        "required": false, 
                        "alwaysSrc": false, 
                        "ddConfig": {
                            "type": "data1d.ospec:in", 
                            "allowedTypes": [
                                "data1d.ospec:out"
                            ]
                        }, 
                        "offsetPosition": {
                            "top": 10, 
                            "left": 0
                        }
                    }, 
                    {
                        "direction": [
                            1, 
                            0
                        ], 
                        "multiple": true, 
                        "name": "output", 
                        "required": false, 
                        "alwaysSrc": true, 
                        "ddConfig": {
                            "type": "data1d.ospec:out", 
                            "allowedTypes": [
                                "data1d.ospec:in"
                            ]
                        }, 
                        "offsetPosition": {
                            "top": 10, 
                            "left": 20
                        }
                    }
                ], 
                "xtype": "WireIt.ImageContainer", 
                "image": "../../static/img/rowantests/qxqz.png", 
                "icon": "../../static/img/rowantests/qxqz.png"
            }, 
            "name": "Two theta to qxqz"
        }
    ], 
    "propertiesFields": [
        {
            "typeInvite": "Enter a title", 
            "type": "string", 
            "name": "name", 
            "label": "Title"
        }, 
        {
            "label": "Description", 
            "type": "text", 
            "name": "description", 
            "cols": 30
        }
    ], 
    "languageName": "NCNR ANDR"
};
