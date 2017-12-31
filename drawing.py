import uuid
import re
import copy

from bs4 import BeautifulSoup

import json_templates

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

        self.eve_x = CSS_LEFT_RE.search(css).group('eve_x')
        self.eve_y = CSS_TOP_RE.search(css).group('eve_y')
        self.text = self.eve_parsed_html.text.strip()

    def get_gns_coordinates(self):
        return self.topology.calculate_gns3_coordinates((self.eve_x, self.eve_y))

    def build_gns_topology_json(self):
        drawing_json = copy.deepcopy(json_templates.DRAWING_JSON_TEMPLATE)
        gns_x, gns_y = self.get_gns_coordinates()

        drawing_json['x'] = gns_x
        drawing_json['y'] = gns_y
        drawing_json['drawing_id'] = str(self.uuid)
        drawing_json['svg'] = self.SVG_TEMPLATE.format(text=self.text)

        return drawing_json

# <html><body><div class="customShape customText context-menu jtk-draggable ui-resizable dragstopped" data-path="1" id="customText1" style="display: inline; position: absolute; left: 1011px; top: 240px; cursor: move; z-index: 1001; height: 75px; width: auto;"><p align="center" class="" contenteditable="false" style="vertical-align: top; color: rgb(0, 0, 0); background-color: rgb(255, 255, 255); font-size: 18.75px; font-weight: normal;">OSPF 11<br/>PHASE 3 DMVPN<br/>802.1S MST        </p><div class="ui-resizable-handle ui-resizable-e" style="z-index: 90; display: block;"></div><div class="ui-resizable-handle ui-resizable-s" style="z-index: 90; display: block;"></div><div class="ui-resizable-handle ui-resizable-se ui-icon ui-icon-gripsmall-diagonal-se" style="z-index: 90; display: block;"></div></div></body></html>

# "svg": "<svg height=\"40\" width=\"150\"><text fill=\"#000000\" fill-opacity=\"1.0\" font-family=\"TypeWriter\" font-size=\"10.0\" font-weight=\"bold\">TO THE LEFT</text></svg>"