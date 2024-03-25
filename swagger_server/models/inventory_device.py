# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.ipv4_addr import Ipv4Addr  # noqa: F401,E501
import re  # noqa: F401,E501
from swagger_server import util


class InventoryDevice(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, ip: Ipv4Addr=None, username: str=None, password: str=None):  # noqa: E501
        """InventoryDevice - a model defined in Swagger

        :param ip: The ip of this InventoryDevice.  # noqa: E501
        :type ip: Ipv4Addr
        :param username: The username of this InventoryDevice.  # noqa: E501
        :type username: str
        :param password: The password of this InventoryDevice.  # noqa: E501
        :type password: str
        """
        self.swagger_types = {
            'ip': Ipv4Addr,
            'username': str,
            'password': str
        }

        self.attribute_map = {
            'ip': 'ip',
            'username': 'username',
            'password': 'password'
        }
        self._ip = ip
        self._username = username
        self._password = password

    @classmethod
    def from_dict(cls, dikt) -> 'InventoryDevice':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The InventoryDevice of this InventoryDevice.  # noqa: E501
        :rtype: InventoryDevice
        """
        return util.deserialize_model(dikt, cls)

    @property
    def ip(self) -> Ipv4Addr:
        """Gets the ip of this InventoryDevice.


        :return: The ip of this InventoryDevice.
        :rtype: Ipv4Addr
        """
        return self._ip

    @ip.setter
    def ip(self, ip: Ipv4Addr):
        """Sets the ip of this InventoryDevice.


        :param ip: The ip of this InventoryDevice.
        :type ip: Ipv4Addr
        """

        self._ip = ip

    @property
    def username(self) -> str:
        """Gets the username of this InventoryDevice.


        :return: The username of this InventoryDevice.
        :rtype: str
        """
        return self._username

    @username.setter
    def username(self, username: str):
        """Sets the username of this InventoryDevice.


        :param username: The username of this InventoryDevice.
        :type username: str
        """

        self._username = username

    @property
    def password(self) -> str:
        """Gets the password of this InventoryDevice.


        :return: The password of this InventoryDevice.
        :rtype: str
        """
        return self._password

    @password.setter
    def password(self, password: str):
        """Sets the password of this InventoryDevice.


        :param password: The password of this InventoryDevice.
        :type password: str
        """

        self._password = password