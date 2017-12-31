# LINK_JSON_TEMPLATE = {
#     "filters": {},
#     "nodes": [
#         {
#             "label": {
#                 "rotation": 0,
#                 "style": "font-family: TypeWriter;font-size: 10;font-weight: bold;fill: #000000;fill-opacity: 1.0;"
#             }
#         },
#         {
#             "label": {
#                 "rotation": 0,
#                 "style": "font-family: TypeWriter;font-size: 10;font-weight: bold;fill: #000000;fill-opacity: 1.0;"
#             }
#         }
#     ],
#     "suspend": False
# }

LINK_JSON_TEMPLATE = {
    "filters": {},
    "suspend": False
}

LINK_NODE_JSON_TEMPLATE = {
    "label": {
        "style": "font-family: TypeWriter;font-size: 10.0;font-weight: bold;fill: #000000;fill-opacity: 1.0;"
    }
}

IOL_JSON_TEMPLATE = {
    "compute_id": "vm",
    "console_type": "telnet",
    "first_port_name": None,
    "height": 45,
    "label": {
        "rotation": 0,
        "style": "font-family: TypeWriter;font-size: 10;font-weight: bold;fill: #000000;fill-opacity: 1.0;"
    },
    "node_type": "iou",
    "port_name_format": "Ethernet{segment0}/{port0}",
    "port_segment_size": 4,
    "properties": {
        "application_id": 10,
        "l1_keepalives": False,
        "nvram": 128,
        "ram": 416,
        "use_default_iou_values": False
    },
    "width": 66,
    "z": 1
}

GENERAL_INFO_JSON_TEMPLATE = {
    "auto_close": True,
    "auto_open": False,
    "auto_start": False,
    "revision": 8,
    "show_grid": False,
    "show_interface_labels": False,
    "show_layers": False,
    "snap_to_grid": False,
    "type": "topology",
    "version": "2.1.0",
    "zoom": 100
}

DRAWING_JSON_TEMPLATE = {
    "rotation": 0,
    "z": 1
}