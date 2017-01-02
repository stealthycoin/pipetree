# MIT License

# Copyright (c) 2016 Morgan McDermott & John Carlyle

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import hashlib
import inspect
import json
from pipetree.exceptions import InvalidArtifactMetadataError

class Artifact(object):
    def __init__(self, pipeline_stage_config, item_type=None):
        # User meta property
        self._meta = {}

        # Artifact tags
        self._tags = []

        # The specific artifacts that were utilized by the stage that produced
        # this artifact
        # ex) {"prev_pipeline_stage/prev_pipeline_item_type": [0xAB224560xAB...],
        #      "prev_pipeline_stage/prev_pipeline_item_type2": [0xAB221020xBF...] }
        self._antecedents = {}

        # Combined hash of the specific artifacts that were utilized by the stage
        # that produced this artifact
        self._dependency_hash = None

        # Creation time of artifact payload. Stored as UNIX epoch time
        self._creation_time = None

        # Hash of the pipeline stage definition JSON
        self._definition_hash = None

        # Specific hash, the production of which varies for different artifact types
        self._specific_hash = None

        # Name of the pipeline stage that produced this artifact
        self._pipeline_stage = pipeline_stage_config.name

        # Name of the type of item 
        self._item_type = item_type

        # Actual artifact payload
        self._payload = None

        # Listing of meta properties for serialization purposes
        self._meta_properties = ["meta", "tags", "antecedents", "creation_time", "definition_hash", "specific_hash", "dependency_hash", "pipeline_stage", "item_type"]
        
        self._process_stage_definition(pipeline_stage_config)

    def _process_stage_definition(self, pipeline_stage_config):
        """
        Populate relevant artifact fields given stage definition dict
        """

        # We'll hash the stage definition to check if it's changed
        props = {}
        ignore = ["parent_class"]
        for prop in dir(pipeline_stage_config):
            value = getattr(pipeline_stage_config, prop)
            if not prop.startswith('__') and not inspect.ismethod(value) and prop not in ignore:
                props[prop] = value

        h = hashlib.md5()
        stage_json = json.dumps(props, sort_keys=True)
        h.update(str(stage_json).encode('utf-8'))
        self._definition_hash = h.digest()
        
    def meta_to_dict(self):
        """
        Convert relevant internal object properties to a dictionary for serialization
        """
        d = {}
        for prop in self._meta_properties:
            value = getattr(self, "_" + prop)
            d[prop] = value
        return d

    def meta_from_dict(self, d):
        """
        Load artifact meta from python dictionary
        """
        for prop in self._meta_properties:
            # Ensure that every meta property is set within the dictionary
            if prop not in d:
                stage = "UNKNOWN STAGE"
                if "pipeline_stage" in d:
                    stage = d["pipeline_stage"]
                raise InvalidArtifactMetadataError(stage=stage, property=prop)
            else:
                setattr(self, "_" + prop, d[prop])
