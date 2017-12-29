import xmltodict
import base64
import shutil
import os
import math
import json
import uuid
import copy

import json_templates
from node import Node, Network


class Topology(object):
    GNS_CANVAS_SCALE = 1
    GNS_OFFSET = 200

    def __init__(self, eve_xml=None, args=None):
        self.uuid = uuid.uuid4()
        self.eve_xml = eve_xml
        self.args = args
        self.gns_canvas_size = (0, 0)

        self.parsed_eve_xml = xmltodict.parse(eve_xml)
        self.links = []
        self.id_to_network = {}
        self.id_to_node = {}

        self.parse_xml()

        self.get_gns_canvas_size()
        self.set_gns3_coordinates()

        self.create_links_from_networks()

    @property
    def nodes(self):
        return self.id_to_node.values()

    @property
    def networks(self):
        return self.id_to_network.values()

    def parse_networks(self):
        """
        TODO:
        Returns:

        """
        networks_dict = self.parsed_eve_xml['lab']['topology']['networks']['network']

        for network_dict in networks_dict:
            eve_network_id = network_dict['@id']
            network = Network(eve_network_id=eve_network_id, topology=self)
            self.id_to_network[eve_network_id] = network

    def parse_nodes(self):
        """
        TODO:
        Converts dictionary with parsed xml to list of Node objects

        Args:
            nodes_dict: dictionary containing parsed xml for nodes
            id_to_network: dictionary where key is network_id and value is Network object

        Returns:
            list of Node objects
            dictionary of id to Node object mapping
        """
        nodes_dict = self.parsed_eve_xml['lab']['topology']['nodes']['node']

        for node_dict in nodes_dict:
            node = Node.from_dict(node_dict, topology=self)

    def parse_configs(self):
        """
        TODO:
        Parses XML containing configs and addes them to Node objects

        Args:
            configs_dict: dictionary with parsed xml configs
            id_to_node: dictionary contaning ID to Node object mapping

        Modifies:
            Node objects - added config attribute
        """
        configs_dict = self.parsed_eve_xml['lab']['objects'][0]['configs']['config']
        for config_dict in configs_dict:
            eve_node_id = config_dict['@id']
            config = base64.b64decode(config_dict['#text'])
            node = self.id_to_node[eve_node_id]
            node.config = config

    def parse_xml(self):
        self.parse_networks()
        self.parse_nodes()
        self.parse_configs()
        self.create_links_from_networks()

    def write_configs(self):
        config_dir_path = os.path.join(self.args.dst_dir, 'configs')

        # deleting configs directory if exists, and creating an empty one
        try:
            shutil.rmtree(config_dir_path)
        except FileNotFoundError:
            pass
        os.makedirs(config_dir_path)

        for node in self.nodes:
            node.write_config_to_dir(config_dir_path)

    def get_gns_canvas_size(self):
        """
        TODO:
        Calculates GNS3 canvas size based on the location of nodes in EVE topology

        Args:
            nodes: list of Node objects

        Returns:
            int - canvas width
            int - canvas height
        """
        max_x = max(node.eve_x for node in self.nodes)
        max_y = max(node.eve_y for node in self.nodes)
        # print(f'max x coordinate: {max_x}, max y coordinate: {max_y}')
        self.gns_canvas_size = (
            math.ceil((max_x * self.GNS_CANVAS_SCALE + self.GNS_OFFSET) / 500) * 500,
            math.ceil((max_y * self.GNS_CANVAS_SCALE + self.GNS_OFFSET) / 500) * 500
        )

    def set_gns3_coordinates(self):
        """

        Returns:

        """
        for node in self.nodes:
            node.set_gns_coordinates(self.gns_canvas_size, self.GNS_CANVAS_SCALE)

    def create_links_from_networks(self):
        for network in self.networks:
            network.convert_to_links()

    def build_gns_topology_json(self):
        result = {'topology': {}}
        links_json = []
        for link in self.links:
            first_adapter_number, first_port_number = link.first_interface.get_adapter_port_number()
            second_adapter_number, second_port_number = link.second_interface.get_adapter_port_number()
            link_json = copy.deepcopy(json_templates.LINK_JSON_TEMPLATE)
            link_json['link_id'] = str(link.uuid)
            first_interface_json = link_json['nodes'][0]
            second_interface_json = link_json['nodes'][1]
            first_interface_json['adapter_number'] = first_adapter_number
            first_interface_json['node_id'] = str(link.first_interface.node.uuid)
            first_interface_json['port_number'] = first_port_number
            first_interface_json['label']['text'] = link.first_interface.eve_name

            second_interface_json['adapter_number'] = second_adapter_number
            second_interface_json['node_id'] = str(link.second_interface.node.uuid)
            second_interface_json['port_number'] = second_port_number
            second_interface_json['label']['text'] = link.second_interface.eve_name

            links_json.append(link_json)
        result['topology']['links'] = links_json

        # "nodes": [
        #     {
        #         "adapter_number": {first_adapter_number},
        #         "label": {
        #             "rotation": 0,
        #             "style": "font-family: TypeWriter;font-size: 10;font-weight: bold;fill: #000000;fill-opacity: 1.0;",
        #             "text": "{first_interface_name}",
        #             "x": -2,
        #             "y": 2
        #         },
        #         "node_id": "{first_node_id}",
        #         "port_number": {first_port_number}
        #     },
        return json.dumps(result, indent=4)

