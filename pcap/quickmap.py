#!/usr/bin/python
# quickmap.py written by Thibault Reuille and slightly modified by Josh Pyorre
# https://github.com/ThibaultReuille/graphiti/blob/master/pack.sh

import pysvg
from pysvg.filter import *
from pysvg.gradient import *
from pysvg.linking import *
from pysvg.script import *
from pysvg.shape import *
from pysvg.structure import *
from pysvg.style import *
from pysvg.text import *
from pysvg.builders import *

import sys
import math
import pygeoip

#map = "map.svg"

'''
continent_colors = {
    "NA" : "#113F8C",
    "SA" : "#E54028",
    "EU" : "#01A4A4",
    "AS" : "#F18D05",
    "AF" : "#32742C",
    "AN" : "#616161",
    "OC" : "#D70060",
    "--" : "#FFFFFF",
    "Unknown" : "#FFFFFF"
}
'''
continent_colors = {
    "NA" : "#FF0000",
    "SA" : "#FF0000",
    "EU" : "#FF0000",
    "AS" : "#FF0000",
    "AF" : "#FF0000",
    "AN" : "#FF0000",
    "OC" : "#FF0000",
    "--" : "#FF0000",
    "Unknown" : "#FFFFFF"
}

def miller(latitude, longitude):
    lat = latitude * math.pi / 180.0
    lon = longitude * math.pi / 180.0
    return [lon, (5.0 / 4.0) * math.log(math.tan(math.pi / 4.0 + 2.0 * lat / 5.0))]

def ip_map_world(maplocation, infile,mapname):
    #gi = pygeoip.GeoIP('../flask/static/geodata/GeoLiteCity.dat', pygeoip.MEMORY_CACHE)
    gi = pygeoip.GeoIP('../flask/static/geodata/GeoLiteCity.dat', pygeoip.MEMORY_CACHE)
    vectors = list()
    for line in infile:
        ip = line.strip()
        try:
            geo = gi.record_by_addr(ip)
            if geo is None:
                continue # Skip IPs that don't have geo information
        except:
            continue
        vectors.append(
            {
                "ip" : ip,
                "continent" : geo["continent"],
                "latitude" : geo["latitude"],
                "longitude" : geo["longitude"]
            })

    s = svg()
    sb = ShapeBuilder()

    bg_width = 2048.0 / 2
    bg_height = 1502.0 / 2
    bg_ratio = bg_width / bg_height
    bg = image(x=0, y=0, width=bg_width, height=bg_height)
    #bg.set_xlink_href('../../static/miller-2048x1502-color.jpg')
    bg.set_xlink_href(maplocation)
    s.addElement(bg)

    max_x = math.pi + math.pi
    max_y = (5.0 / 4.0) * math.log(math.tan(9.0 * math.pi / 20.0));

    #s.addElement(sb.createRect(0, 0, width, height, fill="#000000"))

    r = 2.0
    for v in vectors:
        position = miller(v["latitude"], v["longitude"])
        x = bg_width * (math.pi + position[0]) / max_x 
        y = (bg_height / 2.0)  * (1 - position[1] / max_y)
        #print(v)
        s.addElement(sb.createCircle(x, y, r,
                                     stroke = continent_colors[v["continent"]],
                                     fill = continent_colors[v["continent"]]))
    s.save(mapname)