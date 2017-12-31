import copy
import math
import uuid


import json_templates
import exceptions


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
    def first_interface(self):
        return self.interfaces[0]

    @property
    def second_interface(self):
        return self.interfaces[1]

    @property
    def angle(self):
        node_center_x1, node_center_y1 = self.first_interface.node.symbol_center_coordinates
        node_center_x2, node_center_y2 = self.second_interface.node.symbol_center_coordinates
        return math.degrees(
            math.atan2(node_center_y2 - node_center_y1, node_center_x2 - node_center_x1)
        )

    @staticmethod
    def get_label_rotation(rotation):
        if math.fabs(rotation) > 90:
            if rotation > 0:
                return rotation - 180
            else:
                return rotation + 180
        return rotation

    def get_label_coordinates(self):
        node_center_x1, node_center_y1 = self.first_interface.node.symbol_center_coordinates
        node_center_x2, node_center_y2 = self.second_interface.node.symbol_center_coordinates
        try:
            m = (node_center_y2 - node_center_y1) / (node_center_x2 - node_center_x1)

            def get_label_y(x):
                return m * (x - node_center_x1) + node_center_y1

            node_label_x1 = node_center_x1 + (node_center_x2 - node_center_x1) * 0.1
            node_label_x2 = node_center_x2 - (node_center_x2 - node_center_x1) * 0.1

            node_label_y1 = get_label_y(node_label_x1)
            node_label_y2 = get_label_y(node_label_x2)

        except ZeroDivisionError:
            node_label_x1 = node_label_x2 = node_center_x2
            node_label_y1 = node_center_y1 + (node_center_y2 - node_center_y1) * 0.1
            node_label_y2 = node_center_y2 - (node_center_y2 - node_center_y1) * 0.1

        node_x1, node_y1 = self.first_interface.node.gns_coordinates
        node_x2, node_y2 = self.second_interface.node.gns_coordinates
        first_node_label_coordinates = (int(node_label_x1 - node_x1), int(node_label_y1 - node_y1))
        second_node_label_coordinates = (int(node_label_x2 - node_x2), int(node_label_y2 - node_y2))

        return [first_node_label_coordinates, second_node_label_coordinates]

    def __repr__(self):
        return f'Link(interfaces={self.interfaces})'

    def __str__(self):
        return (f'{self.first_interface.node.name} {self.first_interface.eve_name} <--> '
                f'{self.second_interface.node.name} {self.second_interface.eve_name}')

    def build_gns_topology_json(self):

        link_json = copy.deepcopy(json_templates.LINK_JSON_TEMPLATE)
        link_json['link_id'] = str(self.uuid)
        link_json['nodes'] = []

        angle = self.angle
        label_rotation = self.get_label_rotation(angle)
        label_coordinates = self.get_label_coordinates()
        for i, interface in enumerate(self.interfaces):
            node = interface.node
            link_node_json = copy.deepcopy(json_templates.LINK_NODE_JSON_TEMPLATE)
            adapter_number, port_number = interface.get_adapter_port_number()

            link_node_json['adapter_number'] = adapter_number
            link_node_json['port_number'] = port_number
            link_node_json['node_id'] = str(node.uuid)
            link_node_json['label']['text'] = interface.eve_name
            link_node_json['label']['rotation'] = int(label_rotation)
            link_node_json['label']['x'] = label_coordinates[i][0]
            link_node_json['label']['y'] = label_coordinates[i][1]

            link_json['nodes'].append(link_node_json)

        # print(f'{self.first_interface.node.name} <> {self.second_interface.node.name}: {label_rotation}')

        return link_json