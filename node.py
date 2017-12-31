import collections
import os
import uuid
import re
import copy
import math

import errors
import json_templates

IOL_INTERFACE_NAME_RE = re.compile(r'(?P<base_name>[a-zA-Z]+)(?P<adapter_number>\d+)/(?P<port_number>\d+)')


class Node(object):
    """
    TODO
    """
    L2_IOL_LABEL_COORDINATES = (-4, 46)
    L3_IOL_LABEL_COORDINATES = (8, 46)
    DEFAULT_LABEL_COORDINATES = (5, -25)
    SWITCH_SYMBOL_SIZE = (51, 48)
    ROUTER_SYMBOL_SIZE = (66, 45)

    def __init__(self, eve_node_id, name=None, node_type=None,
                 image_path=None, eve_icon=None, eve_x=None, eve_y=None,
                 ethernet_adapters_number=0, serial_adapters_number=0,
                 interfaces_dict=None, topology=None):
        self.uuid = uuid.uuid4()
        self.eve_node_id = eve_node_id
        self.name = name
        self.node_type = node_type
        self.image_path = image_path
        self.eve_icon = eve_icon
        self.eve_x = eve_x
        self.eve_y = eve_y

        self.serial_adapters_number = serial_adapters_number
        self.ethernet_adapters_number = ethernet_adapters_number

        self.interfaces = []
        self.id_to_interface = {}

        self.topology = topology
        self.topology.id_to_node[eve_node_id] = self

        if interfaces_dict is not None:
            self.parse_interfaces(interfaces_dict)

    @classmethod
    def from_dict(cls, node_dict, topology=None):
        """
        TODO
        Creates a Node object if it does exist based on the node_dict

        Args:
            node_dict: dictionary, obtained from xmltodict representing the node
            id_to_network: dictionary, containing mapping from Network id to Network object
            id_to_node: dictionary, containing mapping from Node id to Node object

        Returns:
            instance of the class Node

        Examples:
            node_dict = {'@name': 'R1', '@eve_node_id': '123'}
            node = Node.from_dict(node_dict, {}, {})
        """
        params = cls.parse_node_dict(node_dict)
        node = topology.id_to_node.get(params['eve_node_id'])
        params['topology'] = topology
        interfaces_dict = node_dict.get('interface', [])

        if node is None:
            params['interfaces_dict'] = interfaces_dict
            # if the node does not yet exist, create a new one using class constructor
            return cls(**params)
        else:
            # if node already exists go through each attribute and set it for the existing object
            for attr, value in params.items():
                setattr(node, attr, value)
            node.parse_interfaces(interfaces_dict)
            return node

    @staticmethod
    def parse_node_dict(node_dict):
        """
        Parses dictionary from xmltodict and returns a new dictionary with different variable names

        Args:
            node_dict: dictionary obtained from xmltodict and containing information about nodes

        Returns:
            dictionary containing class Node attribute names with their values
        """
        params = dict()
        params['name'] = node_dict['@name']
        params['eve_node_id'] = node_dict['@id']
        params['node_type'] = node_dict['@type']  # IOL, QEMU, dynamips?
        params['image_path'] = node_dict['@image']
        params['eve_icon'] = node_dict['@icon']
        params['eve_x'] = int(node_dict['@left'])
        params['eve_y'] = int(node_dict['@top'])
        params['ethernet_adapters_number'] = int(node_dict['@ethernet'])
        params['serial_adapters_number'] = int(node_dict['@serial'])
        return params

    @property
    def role(self):
        if 'router' in self.eve_icon.lower():
            return 'router'
        elif 'switch' in self.eve_icon.lower():
            return 'switch'
        else:
            return None

    def __repr__(self):
        return f'Node(eve_node_id={self.eve_node_id}, name={self.name})'

    def parse_interfaces(self, interfaces_dict):
        """
        TODO
        Goes through each interface in the dictionary and creates Interface objects for them

        Args:
            interfaces_dict: dictionary retrieved from xmltodict containing information about interfaces
            id_to_network: dictionary containing Network id to Network object mapping
            id_to_node: dictionary containing Node id to Node object mapping

        Modifies:
            self.interfaces - adds a new Interface to the list
            id_to_node - adds an id to Node object mapping to the dictionary
            May create a remote Node object and Interface if needed
        """
        def parse_interface_dict(int_dict):
            link_type = int_dict['@type']
            eve_interface_id = int_dict['@id']
            eve_interface_name = int_dict['@name']
            try:
                interface = self.get_interface(eve_interface_id)
                interface.eve_name = eve_interface_name
            except errors.MissingInterface:
                if link_type == 'ethernet':
                    eve_network_id = int_dict['@network_id']
                    eve_network = self.topology.id_to_network.get(eve_network_id)
                    self.create_interface(eve_interface_id=eve_interface_id,
                                          eve_interface_name=eve_interface_name,
                                          eve_network=eve_network)

                elif link_type == 'serial':
                    eve_remote_node_id = int_dict['@remote_id']
                    eve_remote_interface_id = int_dict['@remote_if']
                    remote_node = self.topology.id_to_node.get(eve_remote_node_id)

                    if remote_node is None:
                        # remote node does not exist yet
                        remote_node = Node(eve_node_id=eve_remote_node_id, topology=self.topology)
                    try:
                        remote_interface = remote_node.get_interface(eve_remote_interface_id)
                    except errors.MissingInterface:
                        remote_interface = remote_node.create_interface(
                            eve_interface_id=eve_remote_interface_id,
                            remote_node=self
                        )
                        # I do not update interface details later!

                    local_interface = self.create_interface(
                        eve_interface_id=eve_interface_id,
                        eve_interface_name=eve_interface_name,
                        remote_node=remote_node
                    )

                    remote_interface.remote_node = self

                    # link interfaces between each other
                    local_interface.remote_interface = remote_interface
                    remote_interface.remote_interface = local_interface

                    # create Link object if the link is point to point
                    link = Link(interfaces=(local_interface, remote_interface))
                    local_interface.link = link
                    remote_interface.link = link
                    self.topology.links.append(link)

        # xmltodict will return list if the number of child objects is more than 1 and dictionary otherwise
        # this checks if interfaces_dict is Sequence.
        # Note: list is a sequence, dictionary is not a sequence
        if isinstance(interfaces_dict, collections.Sequence):
            for interface_dict in interfaces_dict:
                parse_interface_dict(interface_dict)
        else:
            parse_interface_dict(interfaces_dict)

    def get_interface(self, interface_id):
        """
        Gets an Interface object based on interface_id

        Args:
            interface_id: string, id of the interface in source xml file

        Returns:
            Interface object having this interface_id if exists

        Raises:
            errors.MissingInterface if interface was not found
        """
        try:
            return self.id_to_interface[interface_id]
        except KeyError:
            raise errors.MissingInterface(
                f'Interface with id {interface_id} does not exist on node with id {self.eve_node_id}'
            )

    def create_interface(self, eve_interface_id, eve_interface_name=None,
                         eve_network=None, remote_node=None,
                         remote_interface=None):
        """
        Creates an Interfaces object and stored it in self.interfaces list

        Args:
            eve_interface_id: string, interface id in source XML file
            eve_interface_name: string, interface name in source XML file
            eve_network: Network object to which an interface is connected
            remote_node: Node object, a Node to which an interface is connected if the link is serial
            remote_interface: Interface object, which belongs to
                a Node to which an interface is connected if the link is serial

        Returns:
            Interface object

        Modifies:
            self.interfaces - adds an Interface object to this list
            self.id_to_interface - adds id to Interface object mapping for quick access
        """
        interface = Interface(eve_id=eve_interface_id,
                              eve_name=eve_interface_name,
                              eve_network=eve_network,
                              node=self,
                              remote_node=remote_node,
                              remote_interface=remote_interface)
        self.id_to_interface[eve_interface_id] = interface
        self.interfaces.append(interface)
        return interface

    @property
    def gns_coordinates(self):
        return self.topology.calculate_gns3_coordinates((self.eve_x, self.eve_y))

    @property
    def gns_image(self):
        if self.node_type == 'iol' and self.role == 'switch' and self.topology.args.l2_iol_image:
            return self.topology.args.l2_iol_image
        elif self.node_type == 'iol' and self.role == 'router' and self.topology.args.l3_iol_image:
            return self.topology.args.l3_iol_image
        else:
            return self.image_path

    @property
    def gns_label_coordinates(self):
        if self.node_type == 'iol' and self.role == 'switch':
            return self.L2_IOL_LABEL_COORDINATES
        elif self.node_type == 'iol' and self.role == 'router':
            return self.L3_IOL_LABEL_COORDINATES
        else:
            return self.DEFAULT_LABEL_COORDINATES

    @property
    def symbol(self):
        if self.role == 'switch':
            return ':/symbols/multilayer_switch.svg'
        elif self.role == 'router':
            return ':/symbols/router.svg'

    @property
    def symbol_size(self):
        if self.role == 'switch':
            return self.SWITCH_SYMBOL_SIZE
        elif self.role == 'router':
            return self.ROUTER_SYMBOL_SIZE

    @property
    def symbol_center_coordinates(self):
        gns_x, gns_y = self.gns_coordinates
        symbol_width, symbol_height = self.symbol_size
        return gns_x + symbol_width / 2, gns_y + symbol_height

    def write_config_to_dir(self, dst_dir):
        """
        Creates a config file for the node in the specified directory on disk

        Args:
            dst_dir: string, destination directory where the file should be written

        Returns:
            None
        """
        filename = f'{self.name}_startup-config.cfg'
        path = os.path.join(dst_dir, filename)
        with open(path, 'wb') as f:
            f.write(self.config)

    def build_gns_topology_json(self):
        if self.node_type == 'iol':
            node_json = copy.deepcopy(json_templates.IOL_JSON_TEMPLATE)
        else:
            raise NotImplementedError("There is no template for the node type {self.node_type}")

        node_json['console'] = self.topology.console_start_port + int(self.eve_node_id)
        node_json['label']['text'] = self.name
        node_json['name'] = self.name
        node_json['node_id'] = str(self.uuid)
        node_json['properties']['ethernet_adapters'] = self.ethernet_adapters_number
        node_json['properties']['serial_adapters'] = self.serial_adapters_number
        node_json['properties']['path'] = self.gns_image
        node_json['symbol'] = self.symbol

        gns_x, gns_y = self.gns_coordinates
        node_json['x'] = gns_x
        node_json['y'] = gns_y

        gns_label_x, gns_label_y = self.gns_label_coordinates
        node_json['label']['x'] = gns_label_x
        node_json['label']['y'] = gns_label_y

        return node_json


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
            raise errors.InvalidLink("A link can't connect more than two interfaces")

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


class Interface(object):
    def __init__(self, eve_id, eve_name, eve_network=None, node=None,
                 remote_node=None, remote_interface=None):
        self.eve_id = eve_id
        self.eve_name = eve_name
        self.eve_network = eve_network
        self.node = node
        if self.eve_network is not None:
            self.eve_network.interfaces.append(self)
        self.link = None
        self.remote_node = remote_node
        self.remote_interface = remote_interface

    def __repr__(self):
        return f'Interface(eve_id={self.eve_id}, eve_name={self.eve_name}, node={self.node})'

    def get_adapter_port_number(self):
        if self.node.node_type == 'iol':
            parsed_values = IOL_INTERFACE_NAME_RE.match(self.eve_name).groupdict()
            return int(parsed_values['adapter_number']), int(parsed_values['port_number'])
        else:
            raise NotImplementedError('This method is valid only for IOL devices')
