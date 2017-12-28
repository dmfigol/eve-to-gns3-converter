#!/usr/bin/env python3
import xmltodict
import argparse
import base64
from pprint import pprint
import shutil
import os
import math
import json

import json_templates
from network_model import Node, Link, Interface, Network, GNS_CANVAS_SCALE, GNS_OFFSET


def get_arguments():
    """
    Creates an argument parser

    Returns:
        parsed ArgumentParser object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--src_topology_file',
                        help='specify source UNL/EVE topology file',
                        type=argparse.FileType('r'))
    parser.add_argument('-d', '--dst_dir',
                        help='specify destination folder for resulting files')
    parser.add_argument('-v', '--verbose', help='increase output verbosity',
                        action='store_true')
    args = parser.parse_args()
    return args


def parse_nodes(nodes_dict, id_to_network):
    """
    Converts dictionary with parsed xml to list of Node objects

    Args:
        nodes_dict: dictionary containing parsed xml for nodes
        id_to_network: dictionary where key is network_id and value is Network object

    Returns:
        list of Node objects
        dictionary of id to Node object mapping
    """
    nodes = []
    id_to_node = {}

    for node_dict in nodes_dict:
        node = Node.from_dict(node_dict, id_to_network, id_to_node)
        print(node)
        nodes.append(node)

    return nodes, id_to_node


def parse_configs(configs_dict, id_to_node):
    """
    Parses XML containing configs and addes them to Node objects

    Args:
        configs_dict: dictionary with parsed xml configs
        id_to_node: dictionary contaning ID to Node object mapping

    Modifies:
        Node objects - added config attribute
    """
    for config_dict in configs_dict:
        eve_node_id = config_dict['@id']
        config = base64.b64decode(config_dict['#text'])
        node = id_to_node[eve_node_id]
        node.config = config


def get_gns_canvas_size(nodes):
    """
    Calculates GNS3 canvas size based on the location of nodes in EVE topology

    Args:
        nodes: list of Node objects

    Returns:
        int - canvas width
        int - canvas height
    """
    max_x = max(node.eve_x for node in nodes)
    max_y = max(node.eve_y for node in nodes)
    # print(f'max x coordinate: {max_x}, max y coordinate: {max_y}')
    return (
        math.ceil((max_x * GNS_CANVAS_SCALE + GNS_OFFSET) / 500) * 500,
        math.ceil((max_y * GNS_CANVAS_SCALE + GNS_OFFSET) / 500) * 500
    )


def build_gns_topology_json(nodes):
    result = {}
    # TODO

    return json.dumps(result, indent=4)


def parse_networks(networks_dict):
    """

    Args:
        networks_dict:

    Returns:

    """
    networks = []
    id_to_network = {}

    for network_dict in networks_dict:
        eve_network_id = network_dict['@id']
        network = Network(eve_network_id=eve_network_id)
        networks.append(network)
        id_to_network[eve_network_id] = network

    return networks, id_to_network


def convert_topology():
    args = get_arguments()

    with args.src_topology_file as f:
        src_topology_file = f.read()

    src_topology_dict = xmltodict.parse(src_topology_file)

    networks, id_to_network = parse_networks(src_topology_dict['lab']['topology']['networks']['network'])

    nodes, id_to_node = parse_nodes(src_topology_dict['lab']['topology']['nodes']['node'],
                                    id_to_network)

    parse_configs(src_topology_dict['lab']['objects'][0]['configs']['config'],
                  id_to_node)

    config_dir_path = os.path.join(args.dst_dir, 'configs')

    try:
        shutil.rmtree(config_dir_path)
    except FileNotFoundError:
        pass
    os.makedirs(config_dir_path)

    gns_canvas_size = get_gns_canvas_size(nodes)
    # print(f'GNS3 canvas size: {gns_canvas_size}')

    for node in nodes:
        node.write_config_to_dir(config_dir_path)

        gns_coordinates = node.get_gns_coordinates(gns_canvas_size)
        node.gns_x, node.gns_y = gns_coordinates
        # print(f'{node.name} GNS3 coordinates: {gns_coordinates}')


def main():
    convert_topology()


if __name__ == '__main__':
    main()
