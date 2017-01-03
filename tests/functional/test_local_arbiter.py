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

import unittest
import json
from tests import isolated_filesystem
from collections import OrderedDict

from pipetree.artifact import Artifact
from pipetree.config import PipelineStageConfig
from pipetree.exceptions import *

from pipetree.arbiter import LocalArbiter


class TestLocalArbiter(unittest.TestCase):
    def setUp(self):
        self.config_filename = 'pipetree.json'
        self.testfile_name = 'testfile'
        self.testfile_contents = "Testfile Contents"
        self.fs = isolated_filesystem()
        self.fs.__enter__()

        with open("./" + self.testfile_name, 'w') as f:
            json.dump(self.testfile_contents, f)

        with open("./" + self.config_filename, 'w') as f:
            json.dump(self.generate_pipeline_config(), f)

        self.arbiter = LocalArbiter("./" + self.config_filename)
        pass

    def tearDown(self):
        self.fs.__exit__(None, None, None)

    def generate_pipeline_config(self):
        return OrderedDict([(
            'StageA', {
                'type': 'LocalFilePipelineStage',
                'filepath': self.testfile_name
            }),
            ('StageB', {
                'inputs': ['StageA'],
                'type': 'ExecutorPipelineStage',
                'execute': 'package.file.function'
            })]
        )

    def test_basic_functionality(self):
        pass
