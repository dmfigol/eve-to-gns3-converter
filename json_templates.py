LINK_JSON_TEMPLATE = '''{
    "filters": {{}},
    "link_id": "{link_id}",
    "nodes": [
        {
            "adapter_number": {local_adapter_number},
            "label": {
                "rotation": 0,
                "style": "font-family: TypeWriter;font-size: 10;font-weight: bold;fill: #000000;fill-opacity: 1.0;",
                "text": "{local_interface_name}",
                "x": -2,
                "y": 2
            },
            "node_id": "{local_node_id}",
            "port_number": {local_port_number}
        },
        {
            "adapter_number": {remote_adapter_number},
            "label": {
                "rotation": 0,
                "style": "font-family: TypeWriter;font-size: 10;font-weight: bold;fill: #000000;fill-opacity: 1.0;",
                "text": "{remote_interface_name}",
                "x": -2,
                "y": 2
            },
            "node_id": "{remote_node_id}",
            "port_number": {remote_port_number}
        }
    ],
    "suspend": false
}'''