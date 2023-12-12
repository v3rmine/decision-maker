import os
from os.path import join

from allennlp.common.testing import AllenNlpTestCase
from allennlp.common.util import ensure_list
from gpsr_command_understanding.models.commands_reader import CommandsDatasetReader


FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestCommandsReader(AllenNlpTestCase):

    def setup(self):
        super().setup_method()
        self.reader = CommandsDatasetReader()
        instances = self.reader.read(join(FIXTURE_DIR, "train.txt"))
        self.instances = ensure_list(instances)

    def test_tokens(self):
        assert len(self.instances) == 9
