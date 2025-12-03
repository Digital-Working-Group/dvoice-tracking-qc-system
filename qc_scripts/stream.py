"""
stream.py
based loosely off of ffmpeg's stream and node classes
"""
import inspect
from datetime import datetime
from collections import defaultdict
from qc_scripts.logger import Logger

class Pipeline:
    """
    String together functions within Nodes to run together
    """
    def __init__(self, name, logger=Logger(), **kwargs):
        self.name = name
        self.nodes = []
        self.logger = logger
        self.all_failures = [] ## key it by the extension
        self.state = {}
        self.ignore_log = kwargs.get('ignore_log', [])
        self.pipeline_input = {}
        self.init_context = self._get_init_context()
        self.start_time = None
        self.end_time = None

    def _get_init_context(self, skip=2):
        """Gets where the pipeline was initialized"""
        stack = inspect.stack()
        if len(stack) > skip:
            frame = stack[skip]
            return frame.function
        return "Unable to get init context"

    def update_state(self, key, value):
        """Used to insert external data into the pipeline"""
        self.state[key] = value
        self.ignore_log.append(key)
        self.pipeline_input[key] = value
        return self

    def add_node(self, node):
        """Add a node to the pipeline."""
        self.nodes.append(node)
        return self

    def run(self):
        """Run the pipeline by passing data through each node sequentially."""
        self.start_time = datetime.now()
        for _, node in enumerate(self.nodes):
            update_state = node.process(self.state)
            self.state.update(update_state)
        self.end_time = datetime.now()
        self.logger.log_pipeline(self)
        self.logger.save_to_json(self)
        return self.state

class Node:
    """ Elements that make up a pipeline """
    def __init__(self, func, input_key="passed", write_output_func=None, **kwargs):
        self.func = func
        self.name = func.__name__
        self.input_key = input_key
        self.kwargs = kwargs
        self.write_output_func = write_output_func
        self.start_time = None
        self.end_time = None

    def execute_func(self, input_data):
        """Override this in subclasses to customize."""
        return self.func(input_data, **self.kwargs)

    def process(self, state):
        """
        Process data
        Returns: passes, failures
        """
        self.start_time = datetime.now()
        input_data = state.get(self.input_key, None)
        results = self.execute_func(input_data)

        state_updates = defaultdict(lambda: defaultdict)
        if isinstance(results, list):
            for result in results:
                key = result['ext']
                value = result['final']
                state_updates[key] = value
        if self.write_output_func is not None:
            self.write_output(input_data, state_updates)
        self.end_time = datetime.now()
        return state_updates

    def write_output(self, input_data, state_updates):
        """Add another output function to create summaries of failed files"""
        write_output_kw = self.kwargs.get('write_output_kw', {})
        self.write_output_func(input_data, state_updates, self.name, **write_output_kw)

class SourceNode(Node):
    """
    Subclass of Node that allows for creating initial data for a pipeline
    """
    def execute_func(self, _):
        """Overriding Node execute_func"""
        return self.func(**self.kwargs)

class FilterNode(Node):
    """
    Subclass of Node that allows for applying filters to a dataset
    -- currently not in use, but leaving in case we want to re-implemet it
    """

class MergeNode(Node):
    """
    Subclass of Node that allows for combining data from two pipelines / sources
    TODO - eventually we might want to add support so that we can take in more than 2 inputs
    """
    def __init__(self, func, input_keys, **kwargs):
        super().__init__(func, input_key=None, **kwargs)
        self.input_keys = input_keys

    def process(self, state):
        self.start_time = datetime.now()
        data1 = state.get(self.input_keys[0], [])
        data2 = state.get(self.input_keys[1], [])
        results = self.func(data1, data2, **self.kwargs)
        state_updates = defaultdict(lambda: defaultdict)
        for result in results:
            key = result['ext']
            value = result['final']
            state_updates[key] = value
        self.end_time = datetime.now()
        return state_updates

class ActionNode(Node):
    """
    This will perform some action function on a list of Nodes (not intended to filter)
    """
    def __init__(self, func, input_keys, **kwargs):
        super().__init__(func, **kwargs)
        self.input_keys = input_keys

    def execute_func(self, input_data):
        """Override this in subclasses to customize."""
        return self.func(input_data, **self.kwargs)

    def process(self, state):
        """
        Process data
        Returns: updates to the state
        """
        self.start_time = datetime.now()
        state_updates = defaultdict(lambda: defaultdict)
        for input_key in self.input_keys:
            input_data = state.get(input_key, None)
            if input_data is None or len(input_data) == 0:
                continue

            results = self.execute_func(input_data)
            if isinstance(results, list):
                for result in results:
                    key = result['ext']
                    value = result['final']
                    state_updates[key] = value
        self.end_time = datetime.now()
        return state_updates
