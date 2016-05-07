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

import json
import logging
import multiprocessing
import threading
import traceback

from oslo_messaging import messaging
from six.moves import queue

from enamel import executor


class _ListenerThread(threading.Thread):
    """
    Simple thread class that does nothing but listen on a particular socket,
    read data from the socket, and add the data to a queue structure.
    """

    def __init__(self, listener):
        super(threading.Thread, self).__init__()
        self._listener = listener
        self._queue = queue.Queue()
        self._stop = threading.Event()
        self.daemon = True
    
    def join(self, timeout=None):
        self._stop.set()
        threading.Thread.join(self, timeout)

    def run(self):
        while not self._stop.isSet():
            message = self.listener.poll()[0]
            self._queue.put(message)

    def message_done(self):
        self._queue.task_done()

    def get_message(self):
        """
        Returns oldest message in the queue, or None if no more queued
        messages.
        """
        try:
            return self._queue.get_nowait()
        except moves.queue.Empty:
            return None


class TaskProcessor(object):
    log = logging.getLogger(__name__)

    def __init__(self, config):
        self._running = False
        self._config = config
        self._topic = config.get('topic')
        self._executors = None
        # The task queue is pushed to by the listener thread and read from the
        # executor processes. There queue entry is of the form tuple(priority,
        # task) where priority is an integer number representing the priority
        # of the type of task.
        self._task_queue = queue.PriorityQueue()
        # The result queue is used to communicate the results of a particular
        # task execution back to the main process. Task executor processes
        # typically save long-running task state to the database, so the only
        # real reason for the result queue is to allow the main worker process
        # to keep a cache of status information about ongoing and completed
        # tasks.
        self._result_queue = queue.Queue()
        self._create_listener()
        self._create_task_execution_pool()

    def stop(self):
        self._running = False
        self._listener.join()
        self._clear_result_queue()
        for p in self._executors:
            p.join()

    def run(self):
        """
        Main execution loop. A listener thread reads messages from a message
        queue socket, constructs task objects from the serialized task
        messages, executes the task object and notifies the message bus of
        success or failure.
        """
        self._running = True
        while self._running:
            task = self._read_task_from_queue()
            msg = "Got {0} task with ID {1} over message bus."
            msg = msg.format(task.action, task.id)
            self.log.debug(msg)

            self._task_queue.put((task.priority, task), block=True, timeout=0.05)
            try:
                result = task.run()
                if not result.has_errors():
                    msg = "{0} task with ID {1} completed successfully."
                    msg = msg = format(task.action, task.id)
                    self.log.info(msg)
                    self._notify_task_success(result)
                else:
                    errors = ["{0}: {1}".format(e.code, e.message)
                              for e in result.errors]
                    err_str = "; ".join(errors)
                    msg = ("{0} task with ID {1} failed to complete "
                           "successfully. Errors: {2}.")
                    msg = msg.format(task.action, task.id, err_str)
                    self.log.error(msg)
                    self._notify_task_failure(result)

        def _create_listener(self):
            """
            Sets up the listener that checks for messages on a particular topic
            queue.
            """
            host = self._config.bind_address
            port = self._config.bind_port
            msg = "Creating listener on {0}:{1} checking queue topic {1}."
            msg = msg.format(host, port, self._topic)
            self.log.debug(msg)

            transport = messaging.get_notification_transport(self._config)
            target = message.Target(topic=self._topic)
            self._listener = _ListenThread(driver.listen(target))
            self._listener.start()

            msg = ("Created listener thread {0} on {1}:{2} "
                   "checking queue topic {3}.")
            thread_id = self._listener.thread_id()
            msg = msg.format(thread_id, host, port, self._topic)
            self.log.info(msg)

        def _read_task_from_queue(self):
            """
            Looks to see if there is a new message on the topic queue and if
            so, reads a serialized message from the queue, unpacks it into a
            Task object and returns the Task object.

            Returns None if there are no messages read from the queue.
            """
            task_msg = self._listener.read_message()
            if task_msg is None:
                return
            
            task = tasks.from_message(task_msg)
            self._listener.message_done()
            return task

        def _create_task_execution_pool(self):
            """
            Creates a set of processes (in order to avoid GIL starvation) that
            handle running tasks that have been created to perform a set of
            steps.

            Since tasks are really isolated from each other, there's no need to
            pass information between task-executing processes, so the overhead
            of using processes versus threads is not an issue.
            """
            num_executors = self._config.num_executors
            msg = "Starting %d enamel task executor processes."
            msg = msg.format(num_executors)
            self.log.debug(msg)
            for x in range(num_executors):
                p = multiprocessing.Process(
                        target=executor.run,
                        args=(self._task_queue, self._result_queue))
                self._executors.append(p)
                p.start()

        def _clear_result_queue(self):
            """
            Simply reads all remaining items from the result queue and discards
            the results.
            """
            while True:
                try:
                    self._result_queue.get()
                except moves.queue.QueueEmpty:
                    pass

        def _notify_task_success(self, result):
            pass

        def _notify_task_failure(self, result):
            pass

