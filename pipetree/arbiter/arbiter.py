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
import asyncio
from pipetree.pipeline import PipelineFactory


class ArbiterBase(object):
    def __init__(self, filepath):
        self._loop = asyncio.get_event_loop()
        self._pipeline = PipelineFactory().generate_pipeline_from_file(filepath)
        self._queue = asyncio.Queue(loop=self._loop)
        self._pipeline.set_arbiter_queue(self._queue)


    def _evaluate_pipeline(self):
        for name, stage in self._pipeline.stages.items():
            self._queue.put_nowait(name)

    def run_event_loop(self):
        raise NotImplementedError


class LocalArbiter(ArbiterBase):
    def __init__(self, filepath):
        super().__init__(filepath)

    async def _listen_to_queue(self):
        try:
            while True:
                data = await self._queue.get()
                print('Read: %s' % data)
        except RuntimeError:
            pass
        finally:
            print('Closing local arbiter queue listener.')

    async def _main(self):
        self._evaluate_pipeline()
        print('Cats are fuzzy')


    def run_event_loop(self):
        try:
            self._loop.run_until_complete(asyncio.wait([
                self._main(),
                self._listen_to_queue()
            ]))
        except KeyboardInterrupt:
            click.echo('\nKeyboard Interrupt: closing event loop.')
        finally:
            self._loop.close()


class RemoteArbiter(ArbiterBase):
    pass
