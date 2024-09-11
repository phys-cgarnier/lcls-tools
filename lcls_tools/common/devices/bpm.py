from datetime import datetime
from pydantic import (
    BaseModel,
    # PositiveFloat,
    SerializeAsAny,
    field_validator,
    conint,
    ValidationError,
)
from typing import (
    Dict,
    List,
    Optional,
    Union,
)
from lcls_tools.common.devices.device import (
    Device,
    ControlInformation,
    Metadata,
    PVSet,
)
from epics import PV

EPICS_ERROR_MESSAGE = "Unable to connect to EPICS."


class BooleanModel(BaseModel):
    value: bool


class IntegerModel(BaseModel):
    value: conint(strict=True)


class BPMPVSet(PVSet):
    TMIT: PV
    X: PV
    Y: PV

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @field_validator("*", mode="before")
    def validate_pv_fields(cls, v: str) -> PV:
        return PV(v)


class BPMControlInformation(ControlInformation):
    PVs: SerializeAsAny[BPMPVSet]
    _ctrl_options: SerializeAsAny[Optional[Dict[str, int]]] = dict()

    def __init__(self, *args, **kwargs):
        super(BPMControlInformation, self).__init__(*args, **kwargs)
        # Get possible options for BPM motr PV, empty dict by default.
        options = self.PVs.position.get_ctrlvars(timeout=1)
        if "enum_strs" in options:
            [
                self._ctrl_options.update({option: i})
                for i, option in enumerate(options["enum_strs"])
            ]

    @property
    def ctrl_options(self):
        return self._ctrl_options


class BPMMetadata(Metadata):
    # material: Optional[str] = None
    # sum_l: Optional[PositiveFloat] = None
    # TODO: Add BPM and BPM infomration here?
    # TODO: Add info on locations for X, Y, U wires

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# Change to BSADevice
class BPM(Device):
    controls_information: SerializeAsAny[BPMControlInformation]
    metadata: SerializeAsAny[BPMMetadata]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    """ Decorators """

    def check_state(f):
        """Decorator to only allow transitions in 'Initialized' state"""

        def decorated(self, *args, **kwargs):
            if self.initialize_status is not True:
                print(f"Unable to perform action, {self} not in Initialized state")
                return
            return f(self, *args, **kwargs)

        return decorated


class BPMCollection(BaseModel):
    BPMs: Dict[str, SerializeAsAny[BPM]]

    @field_validator("bpms", mode="before")
    def validate_BPMs(cls, v) -> Dict[str, BPM]:
        for name, BPM in v.items():
            BPM = dict(BPM)
            # Set name field for BPM
            BPM.update({"name": name})
            v.update({name: BPM})
        return v

    # TODO: can the next two functions get moved out?
    def seconds_since(self, time_to_check: datetime) -> int:
        if not isinstance(time_to_check, datetime):
            raise TypeError("Please provide a datetime object for comparison.")
        return (datetime.now() - time_to_check).seconds

    def _make_BPM_names_list_from_args(
        self, args: Union[str, List[str], None]
    ) -> List[str]:
        BPM_names = args
        if BPM_names:
            if isinstance(BPM_names, str):
                BPM_names = [args]
        else:
            BPM_names = list(self.BPMs.keys())
        return BPM_names