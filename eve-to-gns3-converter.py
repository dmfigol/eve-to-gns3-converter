#!/usr/bin/env python3
import xmltodict
import argparse
import base64
from pprint import pprint
import shutil
import os

class Node(object):
    def __init__(self, node_dict):
        self.node_dict = node_dict
        self.name = self.node_dict['@name']
        self.node_id = self.node_dict['@id']
        self.node_type = self.node_dict['@type']
        self.image = self.node_dict['@image']

    def __repr__(self):
        return f'Node(name={self.name})'

    def write_config_to_dir(self, dst_dir):
        """

        Args:
            dst_dir:

        Returns:

        """
        filename = f'{self.name}_startup-config.cfg'
        path = os.path.join(dst_dir, filename)
        with open(path, 'wb') as f:
            f.write(self.config)


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


def parse_nodes(nodes_dict):
    """
    Converts dictionary with parsed xml to list of Node objects

    Args:
        nodes_dict: dictionary containing parsed xml for nodes

    Returns:
        list of Node objects
        dictionary of id to Node object mapping
    """
    nodes = []
    id_to_node = {}

    for node_dict in nodes_dict:
        node = Node(node_dict)
        nodes.append(node)
        id_to_node[node.node_id] = node

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
        node_id = config_dict['@id']
        config = base64.b64decode(config_dict['#text'])
        node = id_to_node[node_id]
        node.config = config


def main():
    args = get_arguments()

    with args.src_topology_file as f:
        src_topology_file = f.read()

    src_topology_dict = xmltodict.parse(src_topology_file)
    nodes, id_to_node = parse_nodes(src_topology_dict['lab']['topology']['nodes']['node'])
    parse_configs(src_topology_dict['lab']['objects'][0]['configs']['config'],
                  id_to_node)

    config_dir_path = os.path.join(args.dst_dir, 'configs')

    try:
        shutil.rmtree(config_dir_path)
    except FileNotFoundError:
        pass
    os.makedirs(config_dir_path)

    for node in nodes:
        node.write_config_to_dir(config_dir_path)


if __name__ == '__main__':
    main()
