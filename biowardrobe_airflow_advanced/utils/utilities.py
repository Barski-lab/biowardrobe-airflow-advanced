import os
import re
import argparse
import subprocess
from json import loads
from functools import partial
from collections import OrderedDict

from schema_salad.ref_resolver import file_uri

from cwltool.pathmapper import adjustFileObjs, adjustDirObjs, normalizeFilesDirs
from cwltool.process import compute_checksums
from cwltool.stdfsaccess import StdFsAccess


def get_folder(abs_path, permissions=0o0775, exist_ok=True):
    try:
        os.makedirs(abs_path, mode=permissions)
    except os.error as ex:
        if not exist_ok:
            raise
    return abs_path


def export_to_file(data, filename):
    get_folder(os.path.dirname(filename))
    with open(filename, 'w') as output_stream:
        output_stream.write(data)


def run_command(command):
    with open(os.devnull, 'w') as devnull:
        subprocess.check_call(command, shell=True, stdout=devnull)


def norm_path(path):
    return os.path.abspath(os.path.normpath(os.path.normcase(path)))


def get_files(current_dir, filename_pattern=".*"):
    """Files with the identical basenames are overwritten"""
    files_dict = {}
    for root, dirs, files in os.walk(current_dir):
        files_dict.update(
            {filename: os.path.join(root, filename) for filename in files if re.match(filename_pattern, filename)}
        )
    return files_dict


def normalize_args(args, skip_list=[]):
    """Converts all relative path arguments to absolute ones relatively to the current working directory"""
    normalized_args = {}
    for key,value in args.__dict__.items():
        if key not in skip_list:
            normalized_args[key] = value if not value or os.path.isabs(value) else os.path.normpath(os.path.join(os.getcwd(), value))
        else:
            normalized_args[key]=value
    return argparse.Namespace (**normalized_args)


def validate_locations(dictionary, key="location"):
    """
    Raises OSError if failed to validate location
    """
    for k in list(dictionary.keys()):
        if k == key:
            yield dictionary[k]
        elif isinstance(dictionary[k], dict):
            for result in validate_locations(dictionary[k], key):
                if not os.path.exists(result):
                    raise OSError(result)
        elif isinstance(dictionary[k], list):
            for d in dictionary[k]:
                for result in validate_locations(d, key):
                    if not os.path.exists(result):
                        raise OSError(result)


def expand_to_file_uri(job_obj):
    if "location" in job_obj:
        job_obj["location"] = file_uri(job_obj["location"])


def add_details_to_outputs(outputs):
    adjustFileObjs(outputs, expand_to_file_uri)
    adjustDirObjs(outputs, expand_to_file_uri)
    normalizeFilesDirs(outputs)
    adjustFileObjs(outputs, partial(compute_checksums, StdFsAccess("")))


def complete_input(item):
    monitor = {"found_none": False}
    recursive_check(item, monitor)
    return not monitor["found_none"]


def recursive_check(item, monitor):
    if item == 'None' or (isinstance(item, str) and 'None' in item):
        monitor["found_none"] = True
    elif isinstance(item, dict):
        dict((k, v) for k, v in item.items() if recursive_check(v, monitor))
    elif isinstance(item, list):
        list(v for v in item if recursive_check(v, monitor))


def remove_not_set_inputs(job_object):
    job_object_filtered ={}
    for key, value in job_object.items():
        if complete_input(value):
            job_object_filtered[key] = value
    return job_object_filtered


def fill_template(template, kwargs):
    job_object = remove_not_set_inputs(loads(template.replace('\n', ' ').format(**kwargs).
                                             replace("'True'", 'true').replace("'False'", 'false').
                                             replace('"True"', 'true').replace('"False"', 'false')))
    return OrderedDict(sorted(job_object.items()))
