#!/usr/bin/env python3
import argparse
import os
import pathlib

from topology import Topology


def get_arguments():
    """
    Creates an argument parser

    Returns:
        parsed ArgumentParser object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--src_topology_file',
                        help='specify source UNL/EVE topology *.unl file',
                        type=argparse.FileType('r'))
    parser.add_argument('-s', '--src_dir',
                        help='specify source folder containing *.unl files')
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


def convert_topology(src_topology_file, args, src_dir):
    path = pathlib.Path(src_dir)
    dst_dir = args.dst_dir / path.relative_to(*path.parts[:1])
    topology = Topology(eve_xml=src_topology_file, args=args, dst_dir=dst_dir)
    topology.write_configs()
    topology.write_gns_topology_json()


def main():
    args = get_arguments()
    if args.src_topology_file:
        with args.src_topology_file as f:
            src_topology_file = f.read()
        convert_topology(src_topology_file, args)

    elif args.src_dir:
        count = 0
        for root, dirs, files in os.walk(args.src_dir):
            for filename in files:
                if filename.endswith(".unl"):
                    full_path = os.path.join(root, filename)
                    print(f'Parsing {full_path}')
                    with open(full_path) as file:
                        src_topology_file = file.read()
                    convert_topology(src_topology_file, args, root)
                    count += 1

        if not count:
            print("No *.unl files have been found.")


if __name__ == '__main__':
    main()
