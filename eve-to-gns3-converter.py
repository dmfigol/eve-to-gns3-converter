#!/usr/bin/env python3
import argparse
from topology import Topology


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


def main():
    args = get_arguments()

    with args.src_topology_file as f:
        src_topology_file = f.read()

    topology = Topology(eve_xml=src_topology_file, args=args)
    topology.write_configs()
    print(topology.build_gns_topology_json())

    # node_17 = topology.id_to_node['17']
    # for interface in node_17.interfaces:
    #     print(interface.get_adapter_port_num())


if __name__ == '__main__':
    main()
