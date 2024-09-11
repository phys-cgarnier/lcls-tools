from pydantic import BaseModel, SerializeAsAny, ConfigDict, field_validator
from typing import List, Union, Callable, Dict
from epics import PV
from lcls_tools.common.devices.device import Device



class BSADevice(Device):
    pass

