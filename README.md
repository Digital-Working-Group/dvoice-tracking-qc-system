# Digital Voice Tracking and QC System

This repository contains an outline to set up QC (quality control) pipelines and walks through an example QC run, where a schedule record of participant visits are compared against filenames of audio recordings of the participant visits.

| Table of Contents |
|---|
| [Record Database Details](#record-database-details) |
| [Repository Contents](#repository-contents) |
| [Provenance and Logging](#provenance-and-logging) |
| [Installation and Setup](#installation-and-setup) |
| [QC Steps](#qc-steps) |
| [Usage Example](#usage-example) |
| [Citations](#citations) |

## Input CSV Structure
The CSV is structured to be similar to the export from a REDCap project with only one form ("Information Sheet"). The columns of the CSV are described below:
| Fieldname | Description | Example |
|---|---|---|
| record_id | Record ID for that data. For our testing, we chose a format consisting of a Cohort Code (two letters and two numbers) and a Participant ID (five numbers). All record ids are samples only. | AB0012345 |
| date_dc | The date the data was captured (YYYY-MM-DD) | 2025-05-29 |
| tester_id | ID of the tester. | 123 |
| data_loc | The location where the data was collected. | remote |

For an example, see [sample_csv_database.csv](sample_csv_database.csv).

# Repository Contents
This repository contains scripts to build and customize pipelines as well as sample data to follow along with the example presented below. 
To familiarize yourself with this repository, consider exploring:

- [qc_pipelines.py](qc_scripts/qc_pipelines.py): combines scripts by inputting them as nodes to pipelines to build out the structure of the QC
- [stream.py](qc_scripts/stream.py): holds the Pipeline and Node class structures
- [logger.py](qc_scripts/logger.py): handles the saving and logging of pipeline results
- [records.py](qc_scripts/records.py): handles ingesting and formatting records from a database
- [walk.py](qc_scripts/walk.py): walk functions to collect files
- [compare_records.py](qc_scripts/compare_records.py): functions to compare filename information to record field data
- [write_flagged_excel.py](qc_scripts/write_flagged_excel.py): writes excel files for manual review
- [duplicates.py](qc_scripts/duplicates.py): functions to check for duplicates or too many file occurrences
- [destination.py](qc_scripts/destination.py): functions to define destination of files that passed all checks
- [move.py](qc_scripts/move.py): functions to move files
- [clean_dataset.py](qc_scripts/clean_dataset.py): functions to compare to and update the clean dataset of all files that have passed the QC

# Installation and Setup
## Python Requirements
These scripts were developed using Python versions 3.9.6 and 3.13.1. 
Requirements for either Python version can be found in the respective requirements subfolders:
```sh
pip install -r requirements/python3-9-6/requirements.txt ## Python 3.9.6 requirements
pip install -r requirements/python3-13-1/requirements.txt ## Python 3.13.1 requirements
```
License information for each set of requirements.txt can be found in their respective pip-licenses.md in the same folder.

Docker support can be found via the `Dockerfile` and `build_docker.sh` and `run_docker.sh` files.

## Setup Template Files
See [templates](templates/) for the template files you should copy. Copy each one into your root folder and rename by removing *_template* from the filename.

### config.json
`config.json` should be edited to contain the path to the root folder for the [provenance](Provenance-and-Logging) logs (`prov_root`) and the path to the root folder for the clean dataset (`clean_root`).
```json
{
    "prov_root": "provenance/",
    "clean_root": "passed_data/clean_dataset"
}
```

### static.json
`static.json` will initially have only the "clean_dataset" key and will be populated with the relevant filepaths as the pipeline generate files:
```json
{
    "clean_dataset": ""
}
```

### main.py
`main.py` will look identical to [main_template.py](templates/main_template.py) and is the main entrypoint for running the scripts.
```py
"""
main_template.py
Main is not version controlled, so copy over the contents of this file and comment/uncomment code as needed.
"""
import qc_pipelines as qcp

if __name__ == '__main__':
    CSV_RECORDS_KW = {'csv_kwargs': {'csv_filepath': 'sample_csv_database.csv'}}
    qcp.csv_records(**CSV_RECORDS_KW)

    # qcp.pull_comparison_sources()
    # Run only csv_records() [option #1] OR pull_comparison_sources() [option #2]

    WALK_KWARGS = {'walk_kwargs': {'roots': ["sample_data/"]}}
    walk(**WALK_KWARGS)

    CMP_KWARGS = {'flag_kwargs': {'record_end_date': qcp.date(2025, 4, 30)},
        'duplicate_kwargs': {'duplicate_root': 'sample_data/duplicates'},
        'move_kwargs': {'move_back': False}}
    qcp.compare_sources_and_duplicates(**CMP_KWARGS)

    MOVE_KWARGS = {'move_kwargs': {'move_back': False}}
    qcp.move_and_update(**MOVE_KWARGS)

```

# QC Steps

### Compare Sources and Duplicates
This step filters based on some example criteria to ensure that the filenames match the data recorded and that there are no extra or duplicate files.

The specific steps used in this example include:
- Checking that the id_date exists in the record.
- Checking that the tester_id matches the one recorded in the record.
- Checking that no duplicate files exist.
- Checking that no extra files exist.
- Checking that the location in the filename matches the location recorded in the record.

If all of those checks pass, the we create a destination path for the file and add it to the dictionary. JSONs are written for the passed files as well as failures at each node in the pipeline.

1. See `main.compare_sources_and_duplicates()`
    - See [Compare Sources and Duplicates](#compare-sources-and-duplicates) for a usage example.
2. Parameters of note (see CMP_KWARGS in `main.py`):
    - *record_end_date* should be updated with the date that you want your QC to go through.
        - 2025-04-30 was used for our sample output runs, the default is the current date.
        - Any filenames that match a record, but go beyond the record_end_date, will be filtered out.
    - *duplicate_root* should be updated with the desired root folder to move duplicate files to.
    - *move_back* affects the movement of the duplicate files. It should be updated to False (move from their original location to the destination) or True (move from their destination back to their original location) based on the need.
3. This step accomplishes the following:
    - Compares id_dates in filenames to the records
        - If the file is within the date range but there is no match, the script creates an excel file for review.
    - Compares tech_ids to records
        - Writes non-matches to an excel for review
    - Checks for duplicate files
    - Checks that 1 file exists for each id_date
    - Verifies that filename and record locations match
    - Writes destination paths for passed files
4. Failure JSON files are generated and XLSX files containing information on id_date and tech_id record mismatches. 
    - JSONs to check:
        - flag_pipeline_flagged_no_records_example
        - flag_pipeline_flagged_tester_id_mismatch_example
        - flag_pipeline_flagged_tester_id_no_records_example
        - flag_pipeline_extra_files
        - flag_pipeline_duplicates
        - flag_pipeline_location_mismatch
    - XLSXs to check (only written if they are not empty):
        - flagged/no_records_entry
        - flagged/tester_id_mismatch
        - flagged/tester_id_no_records
5. Filename errors should then be resolved.
6. The script can be rerun after corrections are made until failures are solved.

#### Keyword Arguments for compare_sources_and_duplicates()
| variable name | type(s) | description | default value | optional |
|---|---|---|---|---|
| record_end_date | datetime | Cut-off date to check. | The current date | Yes |
| rc_tech_id_fieldname | str | Record tech id fieldname. | 'tester_id'| No |
| rc_date_fieldname | str | Record date fieldname. | 'date_dc' | No |
| records | str | Path to CSV or REDCap records in JSON format. | Output JSON from csv_records() | No |
| ext | str | Filename extension to the output flag excel files.| 'example' | Yes |

### Move and Update
1. See `main.move_and_update()`.
    - See [Move and Update the Clean Dataset](#move-and-update-the-clean-dataset) for a usage example.
    - This step moves files to their final destinations and then updates the clean dataset with all of the files cleaned and moved. 
    - If the kwarg *move_back* is False, it will move the source files to their destinations. If set to True, it will move them back from their intended destinations back to their original source location.
2. After running the move, review the file generated. If the move was interrupted or looks incorrect, change *move_back* in the kwargs to True and rerun the script to move the files back to their original locations.
3. Review the new clean dataset to verify that it looks correct. 

#### Keyword Arguments for move_and_update()
| variable name | type(s) | description | default value | optional |
|---|---|---|---|---|
| src_dst_func | func | Get src and dst for move. | [get_src_dst()](qc_scripts/destination.py) | Yes |
| move_back | bool | Move from src to dst. It should be True to move back to the original location (dst to src). | False | Yes |
| clean_dataset | str | Filepath to the current clean dataset | 'clean_dataset' key in the static.json | No |

# Usage Example

## Sample Data
The sample data provided to run the QC can be found in [sample_data](sample_data/). The recordings themselves are unrelated to the QC process.
```
├── flac
│   ├── BL01_06800_20250508_115_remote_bad_extension.flac
├── m4a
│   ├── BL00-13234_20241217_112_remote.m4a
│   ├── BL01_06800_20250220_115_in-person.m4a
│   ├── BL01_38126_20250108_123_remote.m4a
│   ├── BL01_52631_20241217_115_remote.m4a
│   ├── DC02_58910_20250101_115_remote.m4a
│   ├── DC02_58910_20250303_115_remote.m4a
├── mp3
│   ├── BL01_06800_20251015_115_in-person.mp3
│   ├── DC02_61041_20250507_123_in-person.mp3
│   ├── DC0312566.mp3
├── wav
│   ├── BL01-06800_20250509_112_in-person.wav
│   ├── BL01_04952_20250218_112_in-person.wav
│   ├── BL01_04952_20250218_112_in-person_duplicate.wav
│   ├── BL01_04952_20250218_112_in-person_extra.wav
│   ├── BL01_38126_20250108_in-person.wav
│   ├── DC02_61041_20250407_123_in-person.wav
```

## Sample QC Walkthrough
Note that all resulting JSONs are referenced by their key in `static.json` as individual filenames will change.

This example contains commands to run each step in an interactive python shell, but you may also run each step by running main.py and commenting/uncommenting each function call. 

### Read CSV Records
1. See the following sample:
```python
import qc_pipelines as qcp

if __name__ == '__main__':
    CSV_RECORDS_KW = {'csv_kwargs': {'csv_filepath': 'sample_csv_database.csv'}}
    qcp.csv_records(**CSV_RECORDS_KW)
```
- This will result in two files:
    - `csv_records_pipeline_csv_records`: All records read from the CSV.
    - `csv_records_pipeline_fix_record`: Records that need to be reviewed and corrected.
    - Our sample data result in the flagging of:
        - missing_fields: BL00-13234_20241217, DC02-12432_20241123
        - invalid_id: DC265
- Change `csv_filepath` to the proper filepath to your records CSV.
    - This example compares to the [records database CSV](sample_data/sample_csv_database.csv).

#### Keyword Arguments for csv_records()
| variable name | type(s) | description | default value | optional |
|---|---|---|---|---|
| csv_filepath | str| Filepath to your records CSV. | sample_data/sample_csv_database.csv | No |
| required_fieldnames | list | Fields that require a value. | ['date_dc', 'data_loc'] | Yes |

### Walk Sample Data
1. Run the following commands:
```python
import qc_pipelines as qcp

if __name__ == '__main__':
    WALK_KWARGS = {'walk_kwargs': {'roots': ["sample_data/"]}}
    qcp.walk(**WALK_KWARGS)
```
- This will result in two files:
    - `walk_pipeline_walk`: Files that were found and passed checks.
    - `walk_pipeline_other_walk`: Files containing an unwanted extension or that did not match the filename pattern provided. Our sample data will flag the following files:
        - "sample_data/flac/BL01_06800_20250508_115_remote_bad_extension.flac"
        - "sample_data/m4a/BL00-13234_20241217_112_remote.m4a"
        - "sample_data/mp3/DC0312566.mp3"
        - "sample_data/wav/BL01-06800_20250509_112_in-person.wav",
        - "sample_data/wav/BL01_38126_20250108_in-person.wav"
- Change `roots` to a list of root folders to search for files.

#### Keyword Arguments for walk() 
| variable name | type(s) | description | default value | optional |
|---|---|---|---|---|
| roots | list | Filepaths to crawl. | ["sample_data/"] | No |
| ignore_list | list | Folders to ignore in walk. | [] | Yes |
| keep_exts | tuple | File extensions to look for. | ('wav', 'm4a', 'mp3') | No |
| pattern_list | list | Tuples of regex pattern and indices. | [example_pattern_data()](qc_scripts/utility/pattern.py) | Yes |
| make_kv | func | Defines key-value pairs for walk data. | [match_filename_format()](qc_scripts/walk.py) | Yes |
| walk_kwargs | dict | Any additional walk kwargs. | {'multiple_values': True, 'ext': 'walk'} | Yes |

### Compare Sources and Duplicates
1. In [qc_pipelines.compare_sources_and_duplicates](qc_pipelines.py), update the `record_end_date` in `kwargs` to be your desired end date. For our tests, we used (2025, 4, 30).
2. Run the following commands:
```python
import main
main.compare_sources_and_duplicates()
```
- This will result in 6 files:
    - `flag_pipeline_passed`: Files that passed all checks.
    - `flag_pipeline_flagged_no_records_example`: Filename id_date did not match those found in the records.
        - Also see `flagged/no_records_entry` for an Excel summary.
        - Our sample data will flag DC02-58910_20250101, DS02-61041_20250407, DC02-61041_20250507 and BL01-06800_20251015.
    - `flag_pipeline_flagged_tester_id_mismatch_example`: Filenames where the tester_id did not match those found in the records.
        - Also see `flagged/tester_id_mismatch` for an Excel summary.
        - Our sample data will flag BL01-06800_20250220.
    - `flag_pipeline_duplicates`: Files with same id_date and same contents.
        - Our sample data will flag BL01-04952_20250218.
    - `flag_pipelines_extra_files`: Files with same id_date in the filename, but different contents.
        - Our sample data will flag BL01-04952_20250218.
    - `flag_pipelines_location_mismatch`: Filenames where the location did not match the location recorded in the records.
        - Our sample data will flag BL01-38126_20250108.

### Move and Update the Clean Dataset
1. In [qc_pipelines.move_and_update](qc_pipelines.py), if `move_back` is False, it will move the source files to their destinations. If set to True, it will move them back from their intended destinations back to their original source location.
2. Run the following commands:
```python
import main
main.move_and_update()
```
 - This should move all passed files from the previous step into organized folders within `passed_data/`.
 - You may check and see that the clean dataset found in `passed_data/clean_dataset/` has also been updated with the moved data.

# Provenance and Logging

This repository handles logging using a provenance schema, based loosely off of [RADIFOX](https://github.com/jh-mipc/radifox), which provides an example of provenance applied to imaging. You may edit the log contents by modifying the provenance dictionaries created in [logger.log_pipeline()](qc_scripts/logger.py) and [logger.log_node()](qc_scripts/logger.py).

Our current implementation captures the following:
- Pipeline Data:
    - Pipeline name
    - Start time
    - Duration
    - Pipeline function name
    - Pipeline input
    - Nodes
- Node Data:
    - Node name
    - Start time
    - Duration
    - Node function name
    - Node inputs (kwargs)

Provenance output example:
```json
{
    "commit_hash": "c6f678cae97c63175b4dc7f537548dcd5f88b758",
    "duration": "0:00:00.062552",
    "func_name": "csv_records",
    "nodes": [
        {
            "commit_hash": "c6f678cae97c63175b4dc7f537548dcd5f88b758",
            "duration": "0:00:00.061971",
            "node_func": "<function read_csv_records at 0x000001FB70AD71A0>",
            "node_inputs": {
                "csv_filepath": "sample_csv_database.csv"
            },
            "node_name": "read_csv_records",
            "remote_url": "https://github.com/Digital-Working-Group/qc_system.git",
            "script_path_in_repo": "qc_scripts\\records.py",
            "start_time": "2025-08-27 14:47:40.838339"
        },
        {
            "commit_hash": "c6f678cae97c63175b4dc7f537548dcd5f88b758",
            "duration": "0:00:00.000556",
            "node_func": "<function validate_records at 0x000001FB72BA7920>",
            "node_inputs": {
                "ext": "csv_records",
                "required_fieldnames": [
                    "date_dc",
                    "data_loc"
                ]
            },
            "node_name": "validate_records",
            "remote_url": "https://github.com/Digital-Working-Group/qc_system.git",
            "script_path_in_repo": "qc_scripts\\records.py",
            "start_time": "2025-08-27 14:47:40.900322"
        }
    ],
    "pipeline_input": {},
    "pipeline_name": "csv_records_pipeline",
    "remote_url": "https://github.com/Digital-Working-Group/qc_system.git",
    "script_path_in_repo": "qc_pipelines.py",
    "start_time": "2025-08-27 14:47:40.838331"
}
```
# Citations
```bibtex
@electronic{FHS-BAP-Data-Core:2025,
 author = {FHS-BAP Data Core Team},
 title = {Framingham Heart Study Brain Aging Program (FHS-BAP) Data Core},
 url = {https://fhsbap.bu.edu/},
 urldate = {17.06.2024}
}

@electronic{GRIP-Research:2025,
 author = {Global Research Platforms, LLC},
 title = {GRIP Global Research and Imaging Platform},
 url = {https://www.grip-research.org/},
 urldate = {17.06.2024}
}
```
