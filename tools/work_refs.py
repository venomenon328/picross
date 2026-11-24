"""Closed production and explicitly selected synthetic Git origins."""
import os

TEST_REPO = 'venomenon328/picross-remote-test'
TEST_ID = 1470169013
TEST_JOB = 'pz-current'
FIXTURE = os.environ.get('PICROSS_PW_REMOTE_TEST') == '1'
REPOSITORY = TEST_REPO if FIXTURE else 'venomenon328/picross'
CLEAN_MAIN = ('7d045d1ca5b49a44c1cc6eb28ddba756b8f0b69d' if FIXTURE else
              '9f23a7f9e2d0d4c64b96cd1bc5b709e63f8ccfb0')
