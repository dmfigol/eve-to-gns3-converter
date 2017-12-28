import collections
import os

import errors

GNS_CANVAS_SCALE = 1
GNS_OFFSET = 200


class Node(object):
    """
    TODO
    """
    def __init__(self, eve_node_id, name=None, node_type=None,
                 image=None, eve_icon=None, eve_x=None, eve_y=None,
                 interfaces_dict=None, id_to_network=None, id_to_node=None):
        self.eve_node_id = eve_node_id
        self.name = name
        self.node_type = node_type
        self.image = image
        self.eve_icon = eve_icon
        self.eve_x = eve_x
        self.eve_y = eve_y
        self.interfaces = []
        self.id_to_interface = {}
        id_to_node[eve_node_id] = self
        if interfaces_dict is not None:
            self.parse_interfaces(interfaces_dict, id_to_network, id_to_node)

    @classmethod
    def from_dict(cls, node_dict, id_to_network, id_to_node=None):
        """
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
        node = id_to_node.get(params['eve_node_id'])
        params['id_to_network'] = id_to_network
        params['interfaces_dict'] = node_dict.get('interface', [])
        if node is None:
            # if the node does not yet exist, create a new one using class constructor
            return cls(id_to_node=id_to_node, **params)
        else:
            # if node already exists go through each attribute and set it for the existing object
            for attr, value in params.items():
                setattr(node, attr, value)
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

    def parse_interfaces(self, interfaces_dict, id_to_network=None, id_to_node=None):
        """
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

            if link_type == 'ethernet':
                eve_network_id = int_dict['@network_id']
                eve_network = id_to_network.get(eve_network_id)
                self.create_interface(eve_interface_id=eve_interface_id,
                                      eve_interface_name=eve_interface_name,
                                      eve_network=eve_network)

            elif link_type == 'serial':
                eve_remote_node_id = int_dict['@remote_id']
                eve_remote_interface_id = int_dict['@remote_if']
                remote_node = id_to_node.get(eve_remote_node_id)

                if remote_node is None:
                    # remote node does not exist yet
                    remote_node = Node(eve_node_id=eve_remote_node_id, id_to_node=id_to_node)
                try:
                    remote_interface = remote_node.get_interface(eve_remote_interface_id)
                except errors.MissingInterface:
                    remote_interface = remote_node.create_interface(
                        eve_interface_id=eve_remote_interface_id,
                        remote_node=self
                    )

                local_interface = self.create_interface(
                    eve_interface_id=eve_interface_id,
                    eve_interface_name=eve_interface_name,
                    remote_node=remote_node
                )

                remote_interface.remote_node = self

                # link interfaces between each other
                local_interface.remote_interface = remote_interface
                remote_interface.remote_interface = local_interface

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
            self.id_to_interface[interface_id]
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

    def get_gns_coordinates(self, gns_canvas_size):
        """
        Calculates coodinates of objects in GNS3 based on coordinates in EVE

        Args:
            gns_canvas_size: tuple, contains width and height of GNS3 canvas

        Returns:
            tuple - integer coordinates in GNS3
        """
        gns_canvas_width, gns_canvas_height = gns_canvas_size
        return (
            int(self.eve_x) * GNS_CANVAS_SCALE - gns_canvas_width // 2,
            int(self.eve_y) * GNS_CANVAS_SCALE - gns_canvas_height // 2
        )

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
    def __init__(self, eve_network_id):
        self.eve_network_id = eve_network_id
        self.interfaces = []

    def __repr__(self):
        return f'Network(eve_network_id={self.eve_network_id})'


class Link(object):
    # TODO
    pass


class Interface(object):
    def __init__(self, eve_id, eve_name, eve_network=None, node=None,
                 remote_node=None, remote_interface=None):
        self.eve_id = eve_id
        self.eve_name = eve_name
        self.eve_network = eve_network
        self.node = node
        if self.eve_network is not None:
            self.eve_network.interfaces.append(self)
        self.remote_node = remote_node
        self.remote_interface = remote_interface

    def __repr__(self):
        return f'Interface(eve_name={self.eve_name}, node={self.node})'
