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

import sys
import inspect
from typing import List, Type, Tuple, Dict, Any, Callable

from cq_enclosure_builder.part import Part
from cq_enclosure_builder.parts_factory_protocol import PartsFactoryProtocol

class PartFactoryMeta(type):
    """
    Metaclass for PartFactory.

    See comments in PartFactory for general concepts and usage information.
    """
    NO_DEFAULT_VALUE_IDENTIFIER: str = "(no default value)"

    def register_part(cls, category: str, part_type: str, part_class: Type[Part]) -> None:
        if not category.isidentifier():
            raise ValueError(f"'{category}' is not a valid category name. Category names should be valid Python identifiers.")
        if category not in cls.part_registry:
            cls.part_registry[category] = {}
            # Add the dynamic build method
            method_name = f"build_{category.lower()}"
            setattr(cls, method_name, cls._build_method(category))

            # Add the dynamic method for listing available types
            list_method_name = f"list_types_of_{category.lower()}"
            setattr(cls, list_method_name, cls._list_types_method(category))

            # Add the dynamic method for listing available parameters
            list_params_method_name = f"list_parameters_for_{category.lower()}"
            setattr(cls, list_params_method_name, cls._list_parameters_method(category))
        elif part_type in cls.part_registry[category]:
            existing_class = cls.part_registry[category][part_type]
            module_name = existing_class.__module__
            module = sys.modules[module_name]
            file_path = getattr(module, '__file__', 'Unknown file')
            raise ValueError(f"A part with type '{part_type}' has already been registered for category '{category}' "
                            f"by the class '{existing_class.__name__}' in file '{file_path}'.")
        cls.part_registry[category][part_type] = part_class

    @staticmethod
    def _build_method(category: str):
        """Generate a dynamic `build_x` method for a given category."""
        def method(cls, **kwargs: Any) -> Part:
            return cls.build(category, **kwargs)
        return classmethod(method)

    @staticmethod
    def _list_types_method(category: str):
        """Generate a dynamic `list_types_of_` method for a given category."""
        def method(cls) -> list:
            return cls.list_types_for_category(category)
        return classmethod(method)

    @staticmethod
    def _list_parameters_method(category: str):
        """
        Generate a dynamic `list_parameters_for_x` method for a given category.

        A default_value of None means None was explictly set as the default value;
        if the parameter has no default value, it'll show NO_DEFAULT_VALUE_IDENTIFIER ("(no default value)")
        """
        def method(cls, part_type=None) -> List[dict[str, Any]]:
            part_class = cls.part_registry.get(category, {}).get(part_type or cls.default_types.get(category))
            if not part_class:
                available_part_types_method = getattr(cls, f"list_types_of_{category}", None)
                available_part_types = available_part_types_method() if available_part_types_method else ["COULDN'T RETRIEVE"]
                raise ValueError(f"Unknown part type '{part_type}' for category '{category}'. Available types: {available_part_types}.")

            signature = inspect.signature(part_class.__init__)
            parameters = signature.parameters.items()
            if 'self' not in signature.parameters:
                raise ValueError(f"The '__init__' method of '{part_class.__name__}' must contain a 'self' parameter.")
            parameters = {name: param for name, param in parameters if name != 'self'}

            return [{
                "name": name,
                "default_value": param.default if param.default != param.empty else PartFactoryMeta.NO_DEFAULT_VALUE_IDENTIFIER
            } for name, param in parameters.items()]
        return classmethod(method)

class PartFactory(PartsFactoryProtocol, metaclass=PartFactoryMeta):
    """
    PartFactory is responsible for creating different parts based on their type and category.

    This factory dynamically gets build methods for each registered part category.
    For instance, upon registering a "jack" category, a method named `build_jack` will 
    be added to allow for creating jacks specifically.

    Similarly, a method named `list_types_of_<category>` is generated to list 
    the available types for a given category. For the "jack" category, 
    `list_types_of_jack` will list all registered jack types.

    Usage:
    ------
    - List existing categories: `PartFactory.list_categories()`
    - List available types: `PartFactory.list_types_of_<category>()`
    - List parameters for a part: `PartFactory.list_parameters_for_<category>(part_type="your type")`
        (part_type can be omitted using set_default_types as shown below)
    - Build a part using: `PartFactory.build_<category>(part_type="<some type>", ...args)`
    - A default part type can be set for each category, this way, building the main components for your project is as simple as:
      ```
        from parts import PartFactory as pf
        pf.set_default_types({
            "jack": "my 6.35",
            ...other default parts for categories relevant to your project
        })
        jack_part = pf.build_jack(enclosure_wall_thickness=2)
      ```
    - Register a part with its category and type using the decorator:
      ```
        from .part import Part
        from .parts_factory import register_part

        @register_part("jack", "my 6.35")
        class My635JackPart(Part):
            [...]
      ```
    """

    # Nested dictionary for part registration: {<category> {<type 1>: Class1, <type 2>: Class2}}
    part_registry: Dict[str, Dict[str, Type[Part]]] = {}

    # Stores the default types for each category
    default_types: Dict[str, str] = {}

    # Stores default parameters when building parts
    default_parameters: Dict[str, Any] = {}

    _cache: Dict[Tuple[str, str, Tuple[Tuple[Any, Any]]], Part] = {}

    @classmethod
    def build(cls, category: str, **kwargs: Any) -> Part:
        """Generic build method based on category and part type."""
        part_type = kwargs.pop('part_type', None)
        if not part_type:
            part_type = cls.default_types.get(category)
            if not part_type:
                raise ValueError(f"No part_type provided to build method, and no default provided for category '{category}'. See PartFactory#list_types_of_{category}. See PartFactory#set_default_types.")

        if category not in cls.part_registry:
            raise ValueError(f"Unknown part category: {category}")

        if part_type not in cls.part_registry[category]:
            available_part_types_method = getattr(cls, f"list_types_of_{category}", None)
            available_part_types = available_part_types_method() if available_part_types_method else ["COULDN'T RETRIEVE"]
            raise ValueError(f"Unknown part type '{part_type}' for category '{category}'. Available types: {available_part_types}.")

        # Check the required parameters for that builder using the dynamically generated method
        method_name = f"list_parameters_for_{category.lower()}"
        required_parameters = getattr(cls, method_name)(part_type)

        for param in required_parameters:
            param_name = param["name"]
            if param_name not in kwargs:
                if param_name in cls.default_parameters:
                    kwargs[param_name] = cls.default_parameters[param_name]
                elif param["default_value"] == PartFactoryMeta.NO_DEFAULT_VALUE_IDENTIFIER:
                    raise ValueError(f"Missing required parameter '{param_name}' and no default is set. See PartFactory#set_default_parameters.")
                else:
                    # Adding the default value (from the __init__), because otherwise, not passing a value for a parameter that has a default value,
                    #   and passing a value with explictly the same value as the default value, would result in two different cache entries.
                    kwargs[param_name] = param["default_value"]

        part_instance = None

        # We need to cache lookup after we've added the default params to the kwargs
        cache_key = (category, part_type, tuple(kwargs.items()))
        if cache_key in cls._cache:
            part_instance = cls._cache[cache_key]
        else:
            part_instance = cls.part_registry[category][part_type](**kwargs)
            cls._cache[cache_key] = part_instance

        part_instance.validate()
        return part_instance

    @classmethod
    def list_categories(cls) -> List[str]:
        """List all registered categories."""
        return list(cls.part_registry.keys())

    @classmethod
    def list_types_for_category(cls, category: str) -> List[str]:
        """List all registered types for a given category."""
        return list(cls.part_registry.get(category, {}).keys())

    @classmethod
    def set_default_types(cls, defaults: Dict[str, str]) -> None:
        """Sets the default part type for each category."""
        available_categories = cls.list_categories()

        for category, part_type in defaults.items():
            if category not in available_categories:
                raise ValueError(f"Unknown part category: {category}. Available categories: {available_categories}.")

            available_part_types_method = getattr(cls, f"list_types_of_{category}", None)
            available_part_types = available_part_types_method() if available_part_types_method else ["COULDN'T RETRIEVE"]
            if part_type not in available_part_types:
                raise ValueError(f"Unknown part type '{part_type}' for category '{category}'. Available types: {available_part_types}.")

        cls.default_types.update(defaults)

    @classmethod
    def set_default_parameters(cls, defaults: Dict[str, Any]) -> None:
        """Sets the default parameters for parts."""
        cls.default_parameters.update(defaults)

    @classmethod
    def set_defaults(cls, defaults: Dict[str, Dict]) -> None:
        """Set both the default type for each category, and the default parameters for the parts."""
        cls.set_default_types(defaults["types"])
        cls.set_default_parameters(defaults["parameters"])


def register_part(category: str, part_type: str) -> Callable[[Type[Part]], Type[Part]]:
    """Decorator to register a Part subclass in the PartFactory."""
    def decorator(cls: Type[Part]) -> Type[Part]:
        PartFactory.register_part(category, part_type, cls)
        return cls
    return decorator
