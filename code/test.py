import os
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import json


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

stream = open(os.path.join(__location__, "device-info.yaml"),'r')

data = load(stream, Loader=Loader)
print dump(data)