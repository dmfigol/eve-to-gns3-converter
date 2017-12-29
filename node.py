import collections
import os
import uuid
import re

import errors

IOL_INTERFACE_NAME_RE = re.compile(r'(?P<base_name>[a-zA-Z]+)(?P<adapter_number>\d+)/(?P<port_number>\d+)')

class Node(object):
    """
    TODO
    """
    def __init__(self, eve_node_id, name=None, node_type=None,
                 image=None, eve_icon=None, eve_x=None, eve_y=None,
                 interfaces_dict=None, topology=None):
        self.uuid = uuid.uuid4()
        self.eve_node_id = eve_node_id
        self.name = name
        self.node_type = node_type
        self.image = image
        self.eve_icon = eve_icon
        self.eve_x = eve_x
        self.eve_y = eve_y
        self.gns_x = 0
        self.gns_y = 0
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
        params['image'] = node_dict['@image']
        params['eve_icon'] = node_dict['@icon']
        params['eve_x'] = int(node_dict['@left'])
        params['eve_y'] = int(node_dict['@top'])
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

    def set_gns_coordinates(self, gns_canvas_size, gns_canvas_scale):
        """
        TODO
        Calculates coodinates of objects in GNS3 based on coordinates in EVE

        Args:
            gns_canvas_size: tuple, contains width and height of GNS3 canvas

        Returns:
            tuple - integer coordinates in GNS3
        """
        gns_canvas_width, gns_canvas_height = gns_canvas_size
        self.gns_x = int(self.eve_x) * gns_canvas_scale - gns_canvas_width // 2
        self.gns_y = int(self.eve_y) * gns_canvas_scale - gns_canvas_height // 2

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
            raise errors.NotImplemented("This is not implemented, refer to issue #1 on the github")

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

    def __repr__(self):
        return f'Link(interfaces={self.interfaces})'

    def __str__(self):
        return (f'{self.first_interface.node.name} {self.first_interface.eve_name} <--> '
                f'{self.second_interface.node.name} {self.second_interface.eve_name}')


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
            return parsed_values['adapter_number'], parsed_values['port_number']
        else:
            raise NotImplemented('This method is valid only for IOL devices')
