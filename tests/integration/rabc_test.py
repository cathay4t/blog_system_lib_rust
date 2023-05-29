# SPDX-License-Identifier: Apache-2.0

import logging
import os
import signal
import subprocess
import sys
import time

import pytest

from rabc import RabcClient

DAEMON_MAX_WAIT_TIME = 50   # 5 seconds


@pytest.fixture(scope="session", autouse=True)
def rabc_daemon():
    daemon = subprocess.Popen(
        "rabcd",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid,
    )
    i = 0
    while i < DAEMON_MAX_WAIT_TIME:
        i += 1
        time.sleep(0.1)
        try:
            RabcClient()
            break
        except Exception:
            continue
    yield
    os.killpg(daemon.pid, signal.SIGTERM)


def test_client():
    MAX_REPLY = 5
    POLL_TIMEOUT = 5
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    client = RabcClient()
    reply_count = 0
    while reply_count < MAX_REPLY:
        for event in client.poll(POLL_TIMEOUT):
            reply = client.process(event)
            if reply:
                reply_count += 1
                logging.info(f"Got reply from rabcd '{reply}'")
