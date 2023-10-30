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

from cq_enclosure_builder.parts.common.hole_type import HoleType

class GenericScrewProvider:
    @classmethod
    def build_fastener(cls, screw_class, screw_model_name, screw_size_references, block_sizes, hole_type: HoleType, include_length_param: bool, screw_size_category: str):
        if screw_size_category not in screw_size_references or screw_size_category not in block_sizes:
            raise ValueError(f"Unknown screw size category '{screw_size_category}'; available: {str(list(screw_size_references))}")
            
        screw_size_reference = screw_size_references[screw_size_category]
        fastener = None
        # TODO refactor - need to see more examples of screw constructors
        if include_length_param:
            fastener = screw_class(size=screw_size_reference, fastener_type=screw_model_name, length=20)
        else:
            fastener = screw_class(size=screw_size_reference, fastener_type=screw_model_name)
        block_size = block_sizes[screw_size_category]
    
        return (fastener, block_size, hole_type)

    @classmethod
    def build_counter_sunk_fastener(cls, screw_class, screw_model_name, screw_size_references, counter_sunk_block_sizes, include_length_param: bool, screw_size_category: str):
        if screw_size_category not in screw_size_references or screw_size_category not in counter_sunk_block_sizes:
            raise ValueError(f"Unknown screw size category '{screw_size_category}'; available: {str(list(screw_size_references))}")
            
        screw_size_reference = screw_size_references[screw_size_category]
        cs_fastener = None
        # TODO refactor - need to see more examples of screw constructors
        if include_length_param:
            cs_fastener = screw_class(size=screw_size_reference, fastener_type=screw_model_name, length=20)
        else:
            cs_fastener = screw_class(size=screw_size_reference, fastener_type=screw_model_name)
        counter_sunk_block_size = counter_sunk_block_sizes[screw_size_category]
    
        return (cs_fastener, counter_sunk_block_size)