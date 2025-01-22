from lcls_tools.common.devices.screen import Screen
from lcls_tools.common.image.fit import ImageProjectionFit, ImageFit
from lcls_tools.common.measurements.measurement import Measurement
from pydantic import ConfigDict, SerializeAsAny, field_serializer, field_validator


class ScreenBeamProfileMeasurement(Measurement):
    """
    Class that allows for beam profile measurements and fitting
    ------------------------
    Arguments:
    name: str (name of measurement default is beam_profile),
    device: Screen (device that will be performing the measurement),
    beam_fit: method for performing beam profile fit, default is gfit
    fit_profile: bool = True
    ------------------------
    Methods:
    single_measure: measures device and returns raw and processed image
    measure: does multiple measurements and has an option to fit the image
             profiles

    #TODO: DumpController?
    #TODO: return images flag
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    device: SerializeAsAny[Screen]
    beam_fit: SerializeAsAny[ImageFit] = ImageProjectionFit()
    fit_profile: bool = True

    @field_serializer("beam_fit")
    def ser_fld(self, ele, _info):
        return {"type": ele.__class__.__name__} | ele.model_dump()

    @field_validator("beam_fit", mode="before")
    def validate_beam_fit(cls, v, info):
        if isinstance(v, ImageFit):
            return v
        elif isinstance(v, dict):
            class_ = globals()[v.pop("type")]
            return class_(**v)

    def measure(self, n_shots: int = 1) -> dict:
        """
        Measurement function that takes in n_shots as argument
        where n_shots is the number of image profiles
        we would like to measure. Invokes single_measure per shot,
        storing them in a dictionary sorted by shot number
        Then if self.fit_profile = True, fits the profile of the beam
        and concatenates results with the image dictionary sorted by
        shot number
        """
        images = []
        while len(images) < n_shots:
            images.append(self.device.image)
            # TODO: need to add a wait statement in here for images to update

        results = {"raw_images": images, "fit_results": None}

        if self.fit_profile:
            fit_results = []
            for image in images:
                fit_results += [self.beam_fit.fit_image(image)]

            results["fit_results"] = fit_results

        return results
