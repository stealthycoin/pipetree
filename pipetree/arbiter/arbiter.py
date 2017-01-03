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
import click
import signal
import asyncio
from pipetree.pipeline import PipelineFactory
from concurrent.futures import CancelledError


class ArbiterBase(object):
    def __init__(self, filepath):
        self._loop = asyncio.get_event_loop()
        self._pipeline = PipelineFactory().generate_pipeline_from_file(
            filepath)
        self._queue = asyncio.Queue(loop=self._loop)
        self._pipeline.set_arbiter_queue(self._queue)

    def _evaluate_pipeline(self):
        for name in self._pipeline.endpoints:
            self._pipeline.generate_stage(name, self.enqueue)

    def enqueue(self, obj):
        self._queue.put_nowait(obj)

    def run_event_loop(self):
        raise NotImplementedError


class LocalArbiter(ArbiterBase):
    def __init__(self, filepath):
        super().__init__(filepath)

    @asyncio.coroutine
    def _listen_to_queue(self):
        try:
            while True:
                future = yield from self._queue.get()

                print('Read: %s' % future._input_sources)
        except RuntimeError:
            pass

    @asyncio.coroutine
    def _main(self):
        self._evaluate_pipeline()

    def shutdown(self):
        for task in asyncio.Task.all_tasks():
            task.cancel()

    def run_event_loop(self):
        self._loop.add_signal_handler(signal.SIGHUP, self.shutdown)
        self._loop.add_signal_handler(signal.SIGINT, self.shutdown)
        self._loop.add_signal_handler(signal.SIGTERM, self.shutdown)

        try:
            self._loop.run_until_complete(asyncio.wait([
                self._main(),
                self._listen_to_queue()
            ]))
        except CancelledError:
            click.echo('\nKeyboard Interrupt: closing event loop.')
        finally:
            self._loop.close()


class RemoteArbiter(ArbiterBase):
    pass
