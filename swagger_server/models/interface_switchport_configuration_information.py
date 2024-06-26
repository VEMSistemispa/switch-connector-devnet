# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class InterfaceSwitchportConfigurationInformation(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, mode: str=None, vlans: str=None):  # noqa: E501
        """InterfaceSwitchportConfigurationInformation - a model defined in Swagger

        :param mode: The mode of this InterfaceSwitchportConfigurationInformation.  # noqa: E501
        :type mode: str
        :param vlans: The vlans of this InterfaceSwitchportConfigurationInformation.  # noqa: E501
        :type vlans: str
        """
        self.swagger_types = {
            'mode': str,
            'vlans': str
        }

        self.attribute_map = {
            'mode': 'mode',
            'vlans': 'vlans'
        }
        self._mode = mode
        self._vlans = vlans

    @classmethod
    def from_dict(cls, dikt) -> 'InterfaceSwitchportConfigurationInformation':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The InterfaceSwitchportConfigurationInformation of this InterfaceSwitchportConfigurationInformation.  # noqa: E501
        :rtype: InterfaceSwitchportConfigurationInformation
        """
        return util.deserialize_model(dikt, cls)

    @property
    def mode(self) -> str:
        """Gets the mode of this InterfaceSwitchportConfigurationInformation.


        :return: The mode of this InterfaceSwitchportConfigurationInformation.
        :rtype: str
        """
        return self._mode

    @mode.setter
    def mode(self, mode: str):
        """Sets the mode of this InterfaceSwitchportConfigurationInformation.


        :param mode: The mode of this InterfaceSwitchportConfigurationInformation.
        :type mode: str
        """
        # allowed_values = ["access", "trunk", "static access"]  # noqa: E501
        # if mode not in allowed_values:
        #     raise ValueError(
        #         "Invalid value for `mode` ({0}), must be one of {1}"
        #         .format(mode, allowed_values)
        #     )

        self._mode = mode

    @property
    def vlans(self) -> str:
        """Gets the vlans of this InterfaceSwitchportConfigurationInformation.


        :return: The vlans of this InterfaceSwitchportConfigurationInformation.
        :rtype: str
        """
        return self._vlans

    @vlans.setter
    def vlans(self, vlans: str):
        """Sets the vlans of this InterfaceSwitchportConfigurationInformation.


        :param vlans: The vlans of this InterfaceSwitchportConfigurationInformation.
        :type vlans: str
        """
        if vlans is None:
            raise ValueError("Invalid value for `vlans`, must not be `None`")  # noqa: E501

        self._vlans = vlans
