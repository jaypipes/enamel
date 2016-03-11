#!/usr/bin/env python
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import os
import signal
import sys

import daemon
import extras
from oslo_config import cfg
from oslo_log import log as logging

# NOTE(jaypipes): This code taken from Zuul
# as of python-daemon 1.6 it doesn't bundle pidlockfile anymore
# instead it depends on lockfile-0.9.1 which uses pidfile.
pid_file_module = extras.try_imports(['daemon.pidlockfile', 'daemon.pidfile'])

from enamel import opts
import enamel.task_processor

LOG = logging.getLogger(__name__)


class TaskProcessorApp(object):

    def __init__(self, conf=None):
        self.conf = conf

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Enamel task processor.')
        parser.add_argument('--no-daemon', action='store_true',
                            default=False, help='Do not daemonize.')
        return parser.parse_args()

    def exit_handler(self, signum, frame):
        signal.signal(signal.SIGUSR1, signal.SIG_IGN)
        self.server.stop()

    def run(self):
        self.server = enamel.task_processor.TaskProcessor(self.conf)
        self.server.run()

        # FIXME(cdent): Though this is copied from zuul, I'm pretty
        # sure this is wrong. KILL, TERM, INT might all make sense.
        # USR1 is usually reserved for special user initiated
        # actions like dumping a guru meditation report.
        signal.signal(signal.SIGUSR1, self.exit_handler)
        while True:
            try:
                signal.pause()
            except KeyboardInterrupt:
                msg = "Received ctrl-c: asking {0} to exit nicely...\n"
                msg = msg.format(self.__class__.__name__)
                print(msg)
                self.exit_handler(signal.SIGINT, None)


def setup(args=None):
    if args is None:
        args = []
    conf = cfg.ConfigOpts()
    logging.register_options(conf)
    conf(args, project='enamel')
    logging.setup(conf, 'enamel')
    for group, options in opts.list_opts():
        conf.register_opts(list(options),
                           group=None if group == "DEFAULT" else group)

    return conf


def main():
    conf = setup()
    app = TaskProcessorApp(conf)
    args = app.parse_arguments()

    pid_path = os.path.expanduser(conf.task_processor.pidfile)
    pid = pid_file_module.TimeoutPIDLockFile(pid_path, 10)

    if args.no_daemon:
        app.run()
    else:
        with daemon.DaemonContext(pidfile=pid):
            app.run()


if __name__ == "__main__":
    sys.path.insert(0, '.')
    main()
