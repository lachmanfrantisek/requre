# MIT License
#
# Copyright (c) 2018-2019 Red Hat, Inc.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import shlex
from pathlib import Path
import subprocess
import logging

from requre.exceptions import PersistentStorageException
from requre.storage import PersistentObjectStorage
logger = logging.getLogger(__name__)

STORAGE = PersistentObjectStorage()


def get_if_recording() -> bool:
    """
    True if storage file is set, means that it is requested to use storage.
    """
    return bool(STORAGE.storage_file)


def run_command(cmd, error_message=None, cwd=None, fail=True, output=False):
    """
    subprocess wrapper, copied from packit, for higher level handling of executiong commands,
    :param cmd:
    :param error_message:
    :param cwd:
    :param fail:
    :param output:
    :return:
    """
    if not isinstance(cmd, list):
        cmd = shlex.split(cmd)

    logger.debug("cmd = '%s'", " ".join(cmd))

    cwd = cwd or str(Path.cwd())
    error_message = error_message or f"Command {cmd} failed."

    shell = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
        cwd=cwd,
        universal_newlines=True,
    )

    if not output:
        # output is returned, let the caller process it
        logger.debug("%s", shell.stdout)
    stderr = shell.stderr.strip()
    if stderr:
        logger.error("%s", shell.stderr)

    if shell.returncode != 0:
        logger.error("Command %s failed", shell.args)
        logger.error("%s", error_message)
        if fail:
            raise PersistentStorageException(f"Command {shell.args!r} failed: {error_message}")
        success = False
    else:
        success = True

    if not output:
        return success
    return shell.stdout
