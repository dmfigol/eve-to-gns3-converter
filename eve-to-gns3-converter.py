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
    parser.add_argument('-c', '--console_start_port',
                        help='specify a starting port for console connections, default is 5000',
                        type=int, default=5000)
    parser.add_argument('--l2_iol_image',
                        help='Specify path to L2 IOL image')
    parser.add_argument('--l3_iol_image',
                        help='Specify path to L3 IOL image')

    args = parser.parse_args()
    return args


def main():
    args = get_arguments()
    with args.src_topology_file as f:
        src_topology_file = f.read()

    topology = Topology(eve_xml=src_topology_file, args=args)
    topology.write_configs()
    topology.write_gns_topology_json()


if __name__ == '__main__':
    main()
