import base64
import shutil
import os
import math
import json
import uuid
import copy

import xmltodict

import json_templates
from node import Node
from drawing import Drawing
from connections import Network
from helper import Size


class Topology(object):
    """The class which represents a topology with nodes and links.

    Attributes:
        GNS_SCENE_SCALE (int): constant, scale factor when translating coordinates from EVE to GNS3
        uuid (uuid
    """
    GNS_SCENE_SCALE = 1
    GNS_SCENE_OFFSET = 200
    GNS_DEFAULT_SCENE_SIZE = Size(2000, 1000)

    def __init__(self, eve_xml, args, dst_dir='/dst'):
        self.uuid = uuid.uuid4()
        self.eve_xml = eve_xml
        self.args = args
        self.console_start_port = args.console_start_port
        self.gns_scene_size = None
        self.dst_dir = dst_dir

        self.parsed_eve_xml = xmltodict.parse(eve_xml, force_list={'network', 'interface'})
        self.name = self.parsed_eve_xml['lab']['@name']

        self.links = []
        self.text_objects = []
        self.id_to_network = {}
        self.id_to_node = {}

        self.parse_xml()

        self.calculate_gns_canvas_size()

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
        networks_dict = self.parsed_eve_xml['lab']['topology'].get('networks')
        if networks_dict is not None:
            for network_dict in networks_dict['network']:
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
            Node.from_dict(node_dict, topology=self, )

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
        configs_dict = self.parsed_eve_xml['lab'].get('objects')
        if configs_dict is not None:
            for config_dict in configs_dict[0]['configs']['config']:
                eve_node_id = config_dict['@id']
                config = base64.b64decode(config_dict['#text'])
                node = self.id_to_node[eve_node_id]

                node.config = config

    def parse_text_objects(self):
        """
        TODO:
        Returns:

        """
        text_objects_dict = self.parsed_eve_xml['lab'].get('objects')
        if text_objects_dict is not None:
            for text_object_dict in text_objects_dict[0]['textobjects']['textobject']:
                eve_html = base64.b64decode(text_object_dict['data'])
                self.text_objects.append(Drawing(eve_html=eve_html, topology=self))

    def parse_xml(self):
        self.parse_networks()
        self.parse_nodes()
        self.parse_configs()
        self.parse_text_objects()
        self.create_links_from_networks()

    def write_configs(self):
        config_dir_path = os.path.join(self.dst_dir, self.name, 'configs')

        # deleting configs directory if exists, and creating an empty one
        try:
            shutil.rmtree(config_dir_path)
        except FileNotFoundError:
            pass
        os.makedirs(config_dir_path)

        for node in self.nodes:
            node.write_config_to_dir(config_dir_path)

    def calculate_gns_canvas_size(self):
        """
        TODO:
        Calculates GNS3 canvas size based on the location of nodes in EVE topology

        """
        max_x = max(node.eve_coordinates.x for node in self.nodes)
        max_y = max(node.eve_coordinates.y for node in self.nodes)
        width = math.ceil((max_x * self.GNS_SCENE_SCALE + self.GNS_SCENE_OFFSET) / 500) * 500

        height = math.ceil((max_y * self.GNS_SCENE_SCALE + self.GNS_SCENE_OFFSET) / 500) * 500

        if width < self.GNS_DEFAULT_SCENE_SIZE.width:
            width = self.GNS_DEFAULT_SCENE_SIZE.width
        if height < self.GNS_DEFAULT_SCENE_SIZE.height:
            height = self.GNS_DEFAULT_SCENE_SIZE.height

        self.gns_scene_size = Size(width, height)

    def get_gns_coordinates(self, eve_coordinates):
        return round(eve_coordinates) * self.GNS_SCENE_SCALE - self.gns_scene_size // 2

    def create_links_from_networks(self):
        for network in self.networks:
            network.convert_to_links()

    def build_gns_topology_json(self):
        result = copy.deepcopy(json_templates.GENERAL_INFO_JSON_TEMPLATE)
        result['topology'] = {'computes': []}
        result['topology']['links'] = [link.build_gns_topology_json() for link in self.links]
        result['topology']['nodes'] = [node.build_gns_topology_json() for node in self.nodes]
        result['topology']['drawings'] = [drawing.build_gns_topology_json() for drawing in self.text_objects]

        result['project_id'] = str(self.uuid)
        result['name'] = self.name
        result['scene_width'] = self.gns_scene_size.width
        result['scene_height'] = self.gns_scene_size.height

        return json.dumps(result, indent=4, sort_keys=True)

    def write_gns_topology_json(self):
        result = self.build_gns_topology_json()
        gns_topology_filename = f'{self.name}.gns3'
        gns_topology_file_path = os.path.join(self.dst_dir, self.name, gns_topology_filename)

        with open(gns_topology_file_path, 'w') as f:
            f.write(result)

        print(f'Successfully written topology file at {gns_topology_file_path}')
