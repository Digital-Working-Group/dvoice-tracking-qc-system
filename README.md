# Digital Voice Tracking and QC System

This repository contains an outline to set up QC (quality control) pipelines and walks through an example QC run on a sample REDCap with fictitious participant data.

| Table of Contents |
|---|
| [Record Database Details](#record-database-details) |
| [Repository Contents](#repository-contents) |
| [Provenance and Logging](#provenance-and-logging) |
| [Installation and Setup](#installation-and-setup) |
| [QC Steps](#qc-steps) |
| [Usage Example](#usage-example) |
| [Citations](#citations) |

# Record Database Details
The example QC scripts are designed to ingest a CSV or to pull from REDCap using an API token. To run the QC pipelines, you only need one database for comparison, but both options are outlined below.

## CSV Structure
The CSV is structured to be similar to the export from a REDCap project with only one form ("Information Sheet"). The columns of the CSV are described below:
| Fieldname | Description | Example |
|---|---|---|
| record_id | Record ID for that data. For our testing, we chose a format consisting of a Cohort Code (two letters and two numbers) and a Participant ID (five numbers). All record ids are samples only. | AB0012345 |
| date_dc | The date the data was captured (YYYY-MM-DD) | 2025-05-29 |
| tester_id | ID of the tester. | 123 |
| data_loc | The location where the data was collected. | remote |

For an example, see [sample_csv_database.csv](sample_data/sample_csv_database.csv).

## REDCap Project Structure
To build out your own QC System, see [ProjectStructureExample.REDCap.xml](redcap_example/ProjectStructureExample.REDCap.xml) for a sample REDCap structure. To create a new REDCap project via importing a REDCap XML file, see the [REDCap Setup](#redcap-setup) section for more detailed information.

This project structure has only one form ("Information Sheet") with fields described below:
| Fieldname | Description | Example |
|---|---|---|
| record_id | Record ID for that data. For our testing, we chose a format consisting of a Cohort Code (two letters and two numbers) and a Participant ID (five numbers). All record ids are samples only. | AB0012345 |
| date_dc | The date the data was captured (YYYY-MM-DD) | 2025-05-29 |
| tester_id | ID of the tester. | 123 |
| data_loc | The location where the data was collected. | remote |

REDCap Software Version 15.2.5 - © 2025 Vanderbilt University was utilized for this repository.

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

Example provenance output:
```json
{
    "0": {
        "pipeline_name": "pull_sources_pipeline",
        "start_time": "2025-06-30 12:54:51.507475",
        "duration": "0:00:00.515104",
        "func_name": "pull_comparison_sources",
        "pipeline_input": {},
        "nodes": [
            {
                "node_name": "pull_redcap",
                "start_time": "2025-06-30 12:54:51.507475",
                "duration": "0:00:00.515104",
                "node_func": "<function pull_redcap at 0x000002C7CD36AAF0>",
                "node_inputs": {
                    "fields_list": [
                        "record_id",
                        "date_dc",
                        "tester_id",
                        "data_loc",
                        "information_sheet_complete"
                    ],
                    "token": "read_token",
                    "redcap_url": "https://redcap.bumc.bu.edu/api/"
                },
                "script_path_in_repo": "qc_scripts\\redcap.py",
                "commit_hash": "0f718351a0906ac2b44bfa443d24e0daefbb4b30",
                "remote_url": "https://github.com/Digital-Working-Group/dvoice-tracking-qc-system.git"
            },
            {
                "node_name": "validate_redcap_entries",
                "start_time": "2025-06-30 12:54:52.022579",
                "duration": "0:00:00",
                "node_func": "<function validate_redcap_entries at 0x000002C7CD36A9D0>",
                "node_inputs": {
                    "required_fieldnames": [
                        "date_dc",
                        "data_loc"
                    ]
                },
                "script_path_in_repo": "qc_scripts\\redcap.py",
                "commit_hash": "0f718351a0906ac2b44bfa443d24e0daefbb4b30",
                "remote_url": "https://github.com/Digital-Working-Group/dvoice-tracking-qc-system.git"
            }
        ],
        "script_path_in_repo": "qc_pipelines.py",
        "commit_hash": "0f718351a0906ac2b44bfa443d24e0daefbb4b30",
        "remote_url": "https://github.com/Digital-Working-Group/dvoice-tracking-qc-system.git"
    }
}
```

# Installation and Setup
## Script Setup
These scripts were developed using Python 3.13.1, but have been tested with (CODY + JULIA ADD).
Install the requirements needed to run these scripts:
```sh
pip install -r py3-13-1_requirements.txt
```

See [templates](templates/) for the template files you should copy. Copy each one into your root folder and rename by removing *_template* from the filename. Fill in any filepaths, tokens, or URLs needed.

`config.json` should be edited to contain the path to the root folder for the provenance logs (`prov_root`), the API URL for your REDCap, and the path to the root folder for the clean dataset.

```json
{
    "prov_root": "provenance/",
    "redcap_url": "https://redcap.bumc.bu.edu/api/",
    "clean_root": "passed_data/clean_dataset"
}
```

`static.json` will initially look like the below and each value will be populated with the relevant filepaths as the various parts of the pipeline generate files:

```json
{
    "clean_dataset": "",
    "walk_pipeline_walk": "",
    "walk_pipeline_other_walk": "",
    "csv_records_pipeline_csv_records": "",
    "flag_pipeline_passed": "",
    "flag_pipeline_flagged_no_records_example": "",
    "flag_pipeline_extra_files": "",
    "flag_pipeline_duplicates": "",
    "flag_pipeline_location_mismatch": "",
    "flag_pipeline_flagged_tester_id_mismatch_example": "",
    "flag_pipeline_flagged_tester_id_no_records_example": "",
    "move_pipeline_move": "",
    "move_pipeline_move_move_back": "",
    "csv_records_pipeline_fix_records": ""
}
```

`main.py` will look identical to [main_template.py](templates/main_template.py).

## REDCap Setup
If you are using a REDCap project as your database, you will also need to save your API token.
`read_token.py` should have the `token_loc` variable edited to contain the filepath to a text file that has a single line containing your [REDCap API token](#redcap-api-access).

```py
"""
read_token_template.py
read_token.py is not version controlled because it contains the path to your REDCap token.
"""

def read_token():
    """
    get token
    """
    token_loc = "some_folder/token/token.txt"
    with open(token_loc, 'r') as infile:
        for line in infile:
            return line.strip()
    print("Key not found")
    return None
```

The token text file should look like the below, where TOKEN_VALUE is replaced by the REDCap API token:
```txt
TOKEN_VALUE
```
### REDCap Project Setup
1. Select **New Project**.
2. For the **Project creation option** select *Upload a REDCap project XML file (CDISC ODM format)*. If you would like to use our structure but create your own sample data, use [ProjectStructureExample.REDCAP.xml](redcap_example/ProjectStructureExample.REDCap.xml) or upload with our sample data using [ProjectStructure_with_data.xml](redcap_example/ProjectStructure_with_data.xml).
3. Click **Create Project**.

### REDCap API Access
To gain API access, you'll need to request a token. To do so:
1. Open your REDCap project.
2. Select **User Rights** from the side menu.
3. Select your usr and click **Edit user privileges**.
4. Check the boxes **API Export** and **API Import/Update** and save changes.
5. Click **API** from the side menu.
6. Click **Request API token**. You will recieve an email when your REDCap administrator has approved your request.
7. Once approved, return to **API** from the side menu and you will now see your token. Copy that token and put it in a text file.
8. In `read_token.py`, assign `token_loc` to be the path to the text file holding your REDCap token.
9. In your `config.json`, update your `redcap_url` key to hold your REDCap API URL.

# QC Steps
### Prepare comparison sources
Our example compares to the [records database CSV](sample_data/sample_csv_database.csv) described above, but you may optionally use REDCap instead.
1. See `main.csv_records()`.
    - This reads data from the CSV and reformats it to be keyed by id_date.
    - It then validates the data by checking that the required fields have data.

#### Keyword Arguments for csv_records()
| variable name | type(s) | description | default value | optional |
|---|---|---|---|---|
| csv_filepath | str| Filepath to your records CSV. | No | No |
| required_fieldnames | list | Fields that require a value. | [] | Yes |
| ext | str | filename extension. | "validated_records" | Yes |

### Optional: Use REDCap instead of a CSV
To compare to REDCap instead, you will need to one slight changes to the predefined KWARGS:
    - In `qc_pipelines.compare_sources_and_duplicates()`, change records to grab the filepath associated with the key `pull_sources_pipeline_redcap_records`.
1. See `main.pull_comparison_sources()`.
    - This pulls data from REDCap and reformats it to be keyed by id_date.

#### Keyword Arguments for pull_comparison_sources()
| variable name | type(s) | description | default value | optional |
|---|---|---|---|---|
| fields_list | list | Fields to pull from REDCap. | [] | No |
| token | func | Method that gets token. | No default | No |
| redcap_url | str| REDCap API URL for your project. | No | No |
| required_fieldnames | list | Fields that require a value. | [] | Yes |
| ext | str | filename extension. | "validated_records" | Yes |

### Walk
This step walks over a predefined folder and outputs JSONs to describe files found that matched the walk parameters and all other files found in the given directory (excluding anything from the ignore_list).

1. See `main.walk()`.
    - See [Walk Sample Data](#walk-sample-data) for a usage example.
2. The *walk_pipeline_walk* and *walk_pipeline_other_walk* JSON files (see the updated static.json for filepaths) will contain flagged issues. Issues and resolutions include:
    - Wrong extension type: This file extension wasn't expected, handle accordingly (e.g., Move the file out to a different folder.)
    - No match: Filename did not match the regex. Modify the filename to fit the expected pattern.
    - Invalid date: Verify the date with your team.
3. The script can be rerun until the failures have been resolved. 
    - You may want to move on to the next step before fixing all of these errors if you are waiting on input from team members.

#### Keyword Arguments for walk() 
| variable name | type(s) | description | default value | optional |
|---|---|---|---|---|
| roots | list | Filepaths to crawl. | No default | No |
| ignore_list | list | Files or folders to ignore in walk. | [] | Yes |
| keep_exts | tuple | File extensions to look for. | No default | No |
| pattern_list | list | Tuples of regex pattern and indices. | None | Yes |
| make_kv | func | Defines key-value pairs for walk data. | default_make_kv | Yes |
| walk_kwargs | dict | Any additional walk kwargs. | {} | Yes |

### Compare sources and duplicates
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
2. The kwarg *record_end_date* should be updated with the date that you want your QC to go through.
    - Any filenames that match a record, but go beyond the record_end_date, will be filtered out
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
| record_end_date | datetime | Cut-off date to check. | today | Yes |
| rc_tech_id_fieldname | str | Record tech id fieldname. | No default | No |
| rc_date_fieldname | str | Record date fieldname. | No default | No |
| records | str | Path to CSV or REDCap records in JSON format. | No default | No |
| ext | str | Filename extension (in this case, media type). | No default | Yes |

### Move and update
1. See `main.move_and_update()`.
    - See [Move and Update the Clean Dataset](#move-and-update-the-clean-dataset) for a usage example.
    - This step moves files to their final destinations and then updates the clean dataset with all of the files cleaned and moved. 
    - If the kwarg *move_back* is False, it will move the source files to their destinations. If set to True, it will move them back from their intended destinations back to their original source location.
2. After running the move, review the file generated. If the move was interrupted or looks incorrect, change *move_back* in the kwargs to True and rerun the script to move the files back to their original locations.
3. Review the new clean dataset to verify that it looks correct. 

#### Keyword Arguments for move_and_update()
| variable name | type(s) | description | default value | optional |
|---|---|---|---|---|
| src_dst_func | func | Get src and dst for move. | get_src_dst | Yes |
| move_back | bool | Move from src to dst. It should be True to move back to the original location (dst to src). | False | Yes |
| clean_dataset | str | Filepath to the current clean dataset | No default | No |

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

This example contains commands to run each step in an interactive python shell, but you may also run each step my running main.py and commenting/uncommenting each method call. 

### Read CSV Records
1. Run the following commands:
```python
import main
main.csv_records()
```
- This will result in two files:
    - `csv_records_pipeline_csv_records`: All records read from the CSV.
    - `csv_records_pipeline_fix_record`: Records that need to be reviewed and corrected. Our sample data should flag the record_id DC265 and DC0212432.

### Walk Sample Data
1. Run the following commands:
```python
import main
main.walk()
```
- This will result in two files:
    - `walk_pipeline_walk`: Files that were found and passed checks.
    - `walk_pipeline_other_walk`: Files containing an unwanted extension or that did not match the filename pattern provided. Our sample data will flag the following files:
        - "sample_data/flac/BL01_06800_20250508_115_remote_bad_extension.flac"
        - "sample_data/m4a/BL00-13234_20241217_112_remote.m4a"
        - "sample_data/mp3/DC0312566.mp3"
        - "sample_data/wav/BL01-06800_20250509_112_in-person.wav",
        - "sample_data/wav/BL01_38126_20250108_in-person.wav"

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
1. In [qc_pipelines.move_and_update](qc_pipelines.py), ensure that `move_back` in `kwargs` is set to be `False`.
2. Run the following commands:
```python
import main
main.move_and_update()
```
 - This should move all passed files from the previous step into organized folders within `passed_data/`.
 - You may check and see that the clean dataset found in `passed_data/clean_dataset/` has also been updated with the moved data.

# Citations
```bibtex
@inproceedings{commonvoice:2020,
  author = {Ardila, R. and Branson, M. and Davis, K. and Henretty, M. and Kohler, M. and Meyer, J. and Morais, R. and Saunders, L. and Tyers, F. M. and Weber, G.},
  title = {Common Voice: A Massively-Multilingual Speech Corpus},
  booktitle = {Proceedings of the 12th Conference on Language Resources and Evaluation (LREC 2020)},
  pages = {4211--4215},
  year = 2020
}

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
