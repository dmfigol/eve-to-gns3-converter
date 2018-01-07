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


QEMU_JSON_TEMPLATE = {
    "compute_id": "vm",
    "console_type": "telnet",
    "first_port_name": None,
    "height": 45,
    "label": {
        "rotation": 0,
        "style": "font-family: TypeWriter;font-size: 10.0;font-weight: bold;fill: #000000;fill-opacity: 1.0;"
    },
    "node_type": "qemu",
    "port_segment_size": 0,
    "properties": {
        "acpi_shutdown": False,
        "adapter_type": "e1000",
        "adapters": 8,
        "bios_image": "",
        "bios_image_md5sum": None,
        "boot_priority": "c",
        "cdrom_image": "",
        "cdrom_image_md5sum": None,
        "cpu_throttling": 0,
        "cpus": 1,
        "hda_disk_image": "",
        "hda_disk_image_md5sum": "",
        "hda_disk_interface": "virtio",
        "hdb_disk_image": "",
        "hdb_disk_image_md5sum": None,
        "hdb_disk_interface": "ide",
        "hdc_disk_image": "",
        "hdc_disk_image_md5sum": None,
        "hdc_disk_interface": "ide",
        "hdd_disk_image": "",
        "hdd_disk_image_md5sum": None,
        "hdd_disk_interface": "ide",
        "initrd": "",
        "initrd_md5sum": None,
        "kernel_command_line": "",
        "kernel_image": "",
        "kernel_image_md5sum": None,
        "legacy_networking": False,
        "options": "-nographic",
        "platform": "x86_64",
        "process_priority": "normal",
        "qemu_path": "/usr/bin/qemu-system-x86_64",
        "ram": 768,
        "usage": ""
    },
    "width": 66,
    "z": 0
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
