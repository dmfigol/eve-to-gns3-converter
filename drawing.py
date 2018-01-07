import uuid
import re
import copy

from bs4 import BeautifulSoup

import json_templates
from helper import Point

CSS_LEFT_RE = re.compile(r'left:\s*(?P<eve_x>\d+)')
CSS_TOP_RE = re.compile(r'top:\s*(?P<eve_y>\d+)')


class Drawing(object):
    SVG_TEMPLATE = ("<svg height=\"50\" width=\"150\"><text fill=\"#000000\" fill-opacity=\"1.0\""
                    " font-family=\"TypeWriter\" font-size=\"14.0\" font-weight=\"bold\">"
                    "{text}</text></svg>")

    def __init__(self, eve_html, topology=None):
        self.uuid = uuid.uuid4()
        self.topology = topology

        self.eve_parsed_html = BeautifulSoup(eve_html, 'lxml')
        for br in self.eve_parsed_html.find_all("br"):
            br.replace_with("\n")
        css = self.eve_parsed_html.div['style']

        self.eve_coordinates = Point(int(CSS_LEFT_RE.search(css).group('eve_x')),
                                     int(CSS_TOP_RE.search(css).group('eve_y')))

        self.text = self.eve_parsed_html.text.strip()

    def get_gns_coordinates(self):
        return self.topology.get_gns_coordinates(self.eve_coordinates)

    def build_gns_topology_json(self):
        drawing_json = copy.deepcopy(json_templates.DRAWING_JSON_TEMPLATE)
        gns_coordinates = self.get_gns_coordinates()

        drawing_json['x'] = gns_coordinates.x
        drawing_json['y'] = gns_coordinates.y
        drawing_json['drawing_id'] = str(self.uuid)
        drawing_json['svg'] = self.SVG_TEMPLATE.format(text=self.text)

        return drawing_json