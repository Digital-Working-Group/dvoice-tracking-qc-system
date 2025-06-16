""" logger.py """
import os
import json
import types
import getpass
from pathlib import Path
from datetime import datetime
from qc_scripts.utility.get_latest_data import get_root_fp
from qc_scripts.utility.git import get_git_info_from_caller_script, get_git_info_from_node
from qc_scripts.utility.print import pprint_dict
from qc_scripts.utility.read import read_dictionary_file
from qc_scripts.utility.edit_string import append_to_end
from qc_scripts.utility.log_helper import truncate_max_length, len_dict_list_values

def edit_static_json(static_path, log_path, ext):
        """
        Helper function for save log's static json rewriting
        Reads in provided json and adds specified key:path to it before overwriting.
        """
        static = read_dictionary_file(static_path)
        static[ext] = log_path
        with open(static_path, 'w') as fp:
            json.dump(static, fp, indent=4)

def custom_serializer(obj):
    if isinstance(obj, types.FunctionType):
        return obj.__name__  
    return str(obj)

class Logger:
    """Handles logging QC step results to JSON files."""
    
    def __init__(self, base_dir="save_log", static_path="static.json"):
        # Ensure log directory exists
        os.makedirs(base_dir, exist_ok=True)
        self.base_dir = base_dir
        self.static_path = static_path
    
    def save_to_json(self, pipeline_obj):
        """
        Handles the saving of states to json files
        """
        ## Extract relevant information from pipeline object
        pipeline_name = pipeline_obj.name
        result = pipeline_obj.state
        ignore_log = pipeline_obj.ignore_log
        start_time = pipeline_obj.start_time


        timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(self.base_dir, pipeline_name, timestamp)
        os.makedirs(save_path, exist_ok=True)
        files = []

        for ext, data in result.items():
            ## Skip if we flagged it as something to ignore
            if ext in ignore_log:
                continue

            # Construct filename based on 'ext'
            size = len(data)
            nested_size = None
            if size != 0:
                nested_size = len_dict_list_values(data)
            if nested_size is None:
                filename = os.path.join(save_path, f"{pipeline_name}_({size})_{timestamp}_{ext}.json")
            else:
                filename = os.path.join(save_path, f"{pipeline_name}_({size})_[{nested_size}]_{timestamp}_{ext}.json")


            # Save data to JSON file
            with open(filename, 'w') as f:
                json.dump(data, f, default=custom_serializer, indent=4)

            print(f"Saved log: {filename}")
            files.append(filename)
            edit_static_json(self.static_path, filename, f'{pipeline_name}_{ext}')

        return files 

    def log_pipeline(self, pipeline_obj, **kwargs):
        """
        Logs a pipline and its nodes including
        - github script path
        - commit hash and branch name
        - node/pipeline name
        - function name calling node/pipeline
        - input data
        - list of node names 
        """
        duration = str(pipeline_obj.end_time - pipeline_obj.start_time)
        prov_data = {'pipeline_name': pipeline_obj.name,
                        'start_time': str(pipeline_obj.start_time),
                        'duration': duration,
                        'func_name': str(pipeline_obj.init_context),
                        'pipeline_input': truncate_max_length(pipeline_obj.pipeline_input),
                        'nodes': []
        }
        ## Get commit hash and github path 
        prov_data.update(get_git_info_from_caller_script(abstraction_repo_name='qc_utility'))

        ## Get node info
        for node in pipeline_obj.nodes:
            prov_data['nodes'].append(self.log_node(node))
        
        ## Save to provenance JSON file
        today = datetime.now()
        year_month = today.strftime('%Y%m')
        full = today.strftime('%Y%m%d')
        prov_root = get_root_fp('prov_root')
        prov_fn = f'{prov_root}/{year_month}/{full}/provenance_json_{full}.json'
        prov_file = kwargs.pop('prov_file', prov_fn)
        do_print = kwargs.pop('do_print', True)
        username = getpass.getuser()
        if username.lower() not in os.path.basename(prov_file).lower():
            prov_file = append_to_end(prov_file, f'_{username}')
        if os.path.isfile(prov_file):
            prov_dict = read_dictionary_file(prov_file)
        else:
            Path(prov_file).parent.mkdir(parents=True, exist_ok=True)
            prov_dict = {}
        prov_dict[len(prov_dict)] = prov_data

        with open(prov_file, 'w') as f:
            json.dump(prov_dict, f, default=custom_serializer, indent=4)
        if do_print:
            pprint_dict(prov_data, default=custom_serializer, indent=4)

    def log_node(self, node):
        """
        Gets same information nas log_pipeline but per node
        """
        duration = str(node.end_time - node.start_time)
        ## add node.start_time?
        node_log = {'node_name': node.name,
                    'start_time': str(node.start_time),
                    'duration': duration,
                    'node_func': str(node.func),
                    'node_inputs': truncate_max_length(node.kwargs)
        }

        node_log.update(get_git_info_from_node(node.func))
        return node_log
