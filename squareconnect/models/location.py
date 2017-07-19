# coding: utf-8

"""
Copyright 2017 Square, Inc.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""


from pprint import pformat
from six import iteritems
import re


class Location(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, id=None, name=None, address=None, timezone=None, capabilities=None):
        """
        Location - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'id': 'str',
            'name': 'str',
            'address': 'Address',
            'timezone': 'str',
            'capabilities': 'list[str]'
        }

        self.attribute_map = {
            'id': 'id',
            'name': 'name',
            'address': 'address',
            'timezone': 'timezone',
            'capabilities': 'capabilities'
        }

        self._id = id
        self._name = name
        self._address = address
        self._timezone = timezone
        self._capabilities = capabilities

    @property
    def id(self):
        """
        Gets the id of this Location.
        The location's unique ID.

        :return: The id of this Location.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this Location.
        The location's unique ID.

        :param id: The id of this Location.
        :type: str
        """

        self._id = id

    @property
    def name(self):
        """
        Gets the name of this Location.
        The location's name.

        :return: The name of this Location.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this Location.
        The location's name.

        :param name: The name of this Location.
        :type: str
        """

        self._name = name

    @property
    def address(self):
        """
        Gets the address of this Location.
        The location's physical address.

        :return: The address of this Location.
        :rtype: Address
        """
        return self._address

    @address.setter
    def address(self, address):
        """
        Sets the address of this Location.
        The location's physical address.

        :param address: The address of this Location.
        :type: Address
        """

        self._address = address

    @property
    def timezone(self):
        """
        Gets the timezone of this Location.
        The [IANA Timezone Database](https://www.iana.org/time-zones) identifier for the location's timezone.

        :return: The timezone of this Location.
        :rtype: str
        """
        return self._timezone

    @timezone.setter
    def timezone(self, timezone):
        """
        Sets the timezone of this Location.
        The [IANA Timezone Database](https://www.iana.org/time-zones) identifier for the location's timezone.

        :param timezone: The timezone of this Location.
        :type: str
        """

        self._timezone = timezone

    @property
    def capabilities(self):
        """
        Gets the capabilities of this Location.
        Indicates which Square features are enabled for the location.  See [LocationCapability](#type-locationcapability) for possible values.

        :return: The capabilities of this Location.
        :rtype: list[str]
        """
        return self._capabilities

    @capabilities.setter
    def capabilities(self, capabilities):
        """
        Sets the capabilities of this Location.
        Indicates which Square features are enabled for the location.  See [LocationCapability](#type-locationcapability) for possible values.

        :param capabilities: The capabilities of this Location.
        :type: list[str]
        """

        self._capabilities = capabilities

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
