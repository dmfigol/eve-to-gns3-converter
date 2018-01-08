import copy
import math
import uuid

import json_templates
import exceptions
from helper import Line


class Network(object):
    def __init__(self, eve_network_id, topology=None):
        self.eve_network_id = eve_network_id
        self.topology = topology
        self.interfaces = []

    def convert_to_links(self):
        """
        Creates Link objects from Network objects

        Modifies:
            self.topology object by adding a new link into self.topology.links

        """
        if self.is_point_to_point():
            link = Link(interfaces=self.interfaces)
            self.topology.links.append(link)
        elif not self.interfaces:
            pass
        else:
            raise NotImplementedError("This is not implemented, refer to issue #1 on the github")

    def is_point_to_point(self):
        """
        Checks if only two interfaces are connected to the Network object

        Returns:
            boolean - True only if two interfaces are the part of Network object
        """
        if len(self.interfaces) == 2:
            return True
        return False

    def __repr__(self):
        return f'Network(eve_network_id={self.eve_network_id})'


class Link(object):
    def __init__(self, interfaces=None):
        self.uuid = uuid.uuid4()
        if interfaces is None:
            self.interfaces = []
        else:
            self.interfaces = list(interfaces)

    def add_interface(self, interface):
        if len(self.interfaces) < 2:
            self.interfaces.append(interface)
        else:
            raise exceptions.InvalidLink("A link can't connect more than two interfaces")

    @property
    def interface1(self):
        return self.interfaces[0]

    @property
    def node1(self):
        return self.interface1.node

    @property
    def interface2(self):
        return self.interfaces[1]

    @property
    def node2(self):
        return self.interface2.node

    @property
    def line(self):
        return Line(self.node1.gns_icon_center_coordinates, self.node2.gns_icon_center_coordinates)

    def get_label_coordinates(self, line):
        label_coordinates = line.get_equidistant_points()
        return (label_coordinates[0] - self.node1.gns_coordinates,
                label_coordinates[1] - self.node2.gns_coordinates)

    def __repr__(self):
        return f'Link(interfaces={self.interfaces})'

    def __str__(self):
        return (f'{self.interface1.node.name} {self.interface1.eve_name} <--> '
                f'{self.interface2.node.name} {self.interface2.eve_name}')

    def build_gns_topology_json(self):

        link_json = copy.deepcopy(json_templates.LINK_JSON_TEMPLATE)
        link_json['link_id'] = str(self.uuid)
        link_json['nodes'] = []
        line = self.line
        label_rotation = line.rotation

        label_coordinates = self.get_label_coordinates(line)
        for i, interface in enumerate(self.interfaces):
            node = interface.node
            link_node_json = copy.deepcopy(json_templates.LINK_NODE_JSON_TEMPLATE)
            if node.node_type == 'qemu':
                link_node_json['adapter_number'] = interface.eve_id
                link_node_json['port_number'] = 0
            elif node.node_type == 'iol':
                adapter_number, port_number = interface.get_adapter_port_number()
                link_node_json['adapter_number'] = adapter_number
                link_node_json['port_number'] = port_number
            link_node_json['node_id'] = str(node.uuid)
            link_node_json['label']['text'] = interface.eve_name
            link_node_json['label']['rotation'] = int(label_rotation)
            link_node_json['label']['x'] = label_coordinates[i].x
            link_node_json['label']['y'] = label_coordinates[i].y

            link_json['nodes'].append(link_node_json)

        # print(f'{self.first_interface.node.name} <> {self.second_interface.node.name}: {label_rotation}')

        return link_json
