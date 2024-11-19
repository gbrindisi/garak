# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""REST API generator interface

Generic Module for REST API connections
"""

import json
import logging
from typing import List, Union
import requests

import backoff
import jsonpath_ng
from jsonpath_ng.exceptions import JsonPathParserError

from garak import _config
from garak.exception import APIKeyMissingError, RateLimitHit
from garak.generators.base import Generator

import subprocess
import pprint


class ShellGenerator(Generator):
    """Generic API interface for REST models

    See reference docs for details (https://reference.garak.ai/en/latest/garak.generators.rest.html)
    """

    generator_family_name = "SHELL"

    def __init__(self, config_root=_config):
        self._load_config(config_root)
        self.name = "shell"
        self.supports_multiple_generations = False  # not implemented yet
        self.command = _config.plugins.generators["shell"]["shellGenerator"]["command"]

        super().__init__(name="shell", config_root=config_root)


    def _call_model(
        self, prompt: str, generations_this_call: int = 1
    ) -> List[Union[str, None]]:
        """Individual call to execute a shell command and return it's output

        :param prompt: the input to be placed into the request template and sent to the endpoint
        :type prompt: str
        """
        
        command = f"""
            {self.command} "$(cat <<EOF
{prompt}
EOF
            )"
        """

        # print(command)

        # invoke the shell command and return the output
        try:
            response = subprocess.run(command, shell=True, capture_output=True, check=True)
            response_text = response.stdout.decode("utf-8")
        except subprocess.CalledProcessError as e:
            print(f"Command '{command}' failed with return code {e.returncode}")
            response_text = e.stderr.decode("utf-8")
            print(f"Error output: {response_text}")
            return [None]

        if not response_text:
            print("No output received from the shell command.")
            return [None]

        return [response_text]


DEFAULT_CLASS = "ShellGenerator"
