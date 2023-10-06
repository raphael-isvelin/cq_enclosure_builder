"""
   Copyright 2023 Raphaël Isvelin

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

from typing import Dict, List
from cq_enclosure_builder.part import Part

class PartsFactoryProtocol:
    """
    Class used to silence the IDE warnings arrising from the use of methods added dynamically to the factory.

    The class should ideally contain a set of methods for each category in `PartsFactory.list_categories()`.
    When registering a new category, feel free to add the appropriate methods here (optional):
    - build_<category>
    - list_types_of_<category>
    - list_parameters_for_<category>
    """

    @classmethod
    def build_jack(cls, *args, **kwargs) -> Part: pass
    @classmethod
    def list_types_of_jack(cls, *args) -> List[str]: pass
    @classmethod
    def list_parameters_for_jack(cls, *args, **kwargs) -> List[Dict[str, any]]: pass

    @classmethod
    def build_usb_a(cls, *args, **kwargs) -> Part: pass
    @classmethod
    def list_types_of_usb_a(cls, *args) -> List[str]: pass
    @classmethod
    def list_parameters_for_usb_a(cls, *args, **kwargs) -> List[Dict[str, any]]: pass

    @classmethod
    def build_usb_c(cls, *args, **kwargs) -> Part: pass
    @classmethod
    def list_types_of_usb_c(cls, *args) -> List[str]: pass
    @classmethod
    def list_parameters_for_usb_c(cls, *args, **kwargs) -> List[Dict[str, any]]: pass

    @classmethod
    def build_x(cls, *args, **kwargs) -> Part: pass
    @classmethod
    def list_types_of_x(cls, *args) -> List[str]: pass
    @classmethod
    def list_parameters_for_x(cls, *args, **kwargs) -> List[Dict[str, any]]: pass
