# Digital Voice Tracking and QC System

This repository contains an outline to set up QC (quality control) pipelines and walks through an example QC run on a sample REDCap with fictitious participant data.

| Table of Contents |
|---|
| [Introduction](#introduction) |
| [REDCap Details](#redcap-details) |
| [Repository Contents](#repository-contents) |
| [Provenance and Logging](#provenance-and-logging) |
| [Installation and Setup](#installation-and-setup) |
| [QC Steps](#qc-steps) |
| [Usage Example](#usage-example) |
| [Citations](#citations) |

# REDCap Details
## Project Structure
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
- [redcap.py](qc_scripts/redcap.py): handles pulling and validating REDCap records
- [walk.py](qc_scripts/walk.py): walk functions to collect files
- [compare_redcap.py](qc_scripts/compare_redcap.py): functions to compare filename information to REDCap field data
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

# Installation and Setup
## Script Setup
These scripts were developed using Python 3.13.1, but have been tested with (CODY + JULIA ADD).
Install the requirements needed to run these scripts:
```sh
pip install -r py3-13-1_requirements.txt
```

See [templates](templates/) for the template files you should copy. Copy each one into your root folder and rename by removing *template* from the filename. Fill in any filepaths, tokens, or URLs needed.

## REDCap Setup
1. Select **New Project**.
2. For the **Project creation option** select *Upload a REDCap project XML file (CDISC ODM format)*. If you would like to use our structure but create your own sample data, use [ProjectStructureExample.REDCAP.xml](redcap_example/ProjectStructureExample.REDCap.xml) or upload with our sample data using [ProjectStructure_with_data.xml](redcap_example/ProjectStructure_with_data.xml).
3. Click **Create Project**.

# QC Steps
### Prepare comparison sources
Our example only compares to REDCap, but you may wish to add additional nodes to compare with other data sources.
1. Run `pull_comparison_sources()` from `main()`
    - This pulls data from REDCap and reformats it to be keyed by id_date.

#### KWARGS
| variable name | type(s) | description | default value | optional |
|---|---|---|---|---|
| fields_list | list | Fields to pull from REDCap. | [] | No |
| token | func | Method that gets token. | No default | No |
| settings | dict | Dictionary containing any additional actions to be performed on the request. | {} | Yes |
| redcap_url | str| REDCap API URL for your project. | No | No |

### Walk
This step walks over a predefined folder and outputs JSONs to describe files found that matched the walk parameters and all other files found in the given directory (excluding anything from the ignore_list).

1. Run `walk` from `main()`
2. Check the *walk_pipeline_walk* and *walk_pipeline_other_walk* JSON files (see the updated static.json for filepaths) to resolve any issues. Issues and resolutions include:
    - Wrong extension type: This file extension wasn't expected, handle accordingly (e.g., Move the file out to a different folder.)
    - No match: Filename did not match the regex. Modify the filename to fit the expected pattern.
    - Invalid date: Verify the date with your team.
3. Rerun the script until the failures have been resolved. 
    - You may want to move on to the next step before fixing all of these errors if you are waiting on input from team members.

#### `qc_scripts.walk.qc_walk()` Keyword arguments used in `qc_pipelines.walk()`
| variable name | type(s) | description | default value | optional |
|---|---|---|---|---|
| roots | list | Filepaths to crawl. | No default | No |
| ignore_list | list | Files or folders to ignore in walk. | [] | Yes |
| keep_exts | tuple | File extensions to look for. | No default | No |
| pattern_list | list | Tuples of regex pattern and indices. | None | Yes |
| make_kv | func | Defines key-value pairs for walk data. | default_make_kv | Yes |
| walk_kwargs | dict | Any additional walk kwargs. | {} | Yes |

### Compare sources and duplicates
This step filters based on some example criteria to ensure that the filenames match the data recorded on REDCap and that there are no extra or duplicate files. The specific steps used in this example include:
    - Checking that the id_date exists on REDCap.
    - Checking that the tester_id matches the one recorded on REDCap.
    - Checking that no duplicate files exist.
    - Checking that no extra files exist.
    - Checking that the location in the filename matches the location recorded on REDCap.
If all of those checks pass, the we create a destination path for the file and add it to the dictionary. JSONs are written for the passed files as well as failures at each node in the pipeline.

1. Update the kwargs *record_end_date* with the date that you want your QC to go through.
2. Run `compare_sources_and_duplicates()` from `main()`
    - Compares id_dates in filenames to REDCap
        - If the file is within the date range but there is no match, the script creates an excel file for review.
    - Compares tech_ids to REDCap
        - Writes non-matches to an excel for review
    - Checks for duplicate files
    - Checks that one 1 file exists for each id_date
    - Verifies that filename and REDCap locations match
    - Writes destination paths for passed files
3. Check all the failure files generated, including the excels generated for id_date and tech_id REDCap mismatches. 
    - JSONs to check:
        - flag_pipeline_flagged_no_redcap_entry_example
        - flag_pipeline_flagged_not_in_date_range_example
        - flag_pipeline_flagged_tester_id_mismatch_example
        - flag_pipeline_flagged_tester_id_no_redcap_example
        - flag_pipeline_extra_files
        - flag_pipeline_duplicates
        - flag_pipeline_location_mismatch
    - xlsx to check (only written if they are not empty):
        - /flagged/no_redcap_entry
        - /flagged/tester_id_mismatch
        - /flagged/tester_id_no_redcap
4. Fix all filenames where you can easily determine the error or work with your team to resolve remaining errors.
5. Re-run script after corrections are made and continue checking and re-running until failures are solved.

#### KWARGS
| variable name | type(s) | description | default value | optional |
|---|---|---|---|---|
| redcap_entries | str | Path to REDCap pull from step_0. | No default | No |
| record_end_date | DT obj | Cut-off date to check. | today | Yes |
| rc_tech_id_fieldname | str | REDCap fieldname from PVT. | No default | No |
| rc_date_fieldname | str | REDCap date fieldname from PVT. | No default | No |
| ext | str | Filename extension (in this case, media type). | No default | Yes |


### Move and update
1. Ensure that the KWARG `move_back` is set to False
2. Run `move_and_update()` from `main()`
    - This step moves files to their final destinations and then updates the clean dataset with all of the files cleaned and moved. 
3. After running the move, review the file generated. If the move was interrupted or looks incorrect, change *move_back* in the kwargs to True.
4. Review the new clean dataset to verify that it looks correct. 

#### KWARGS
| variable name | type(s) | description | default value | optional |
|---|---|---|---|---|
| src_dst_func | func | Get src and dst for move. | get_src_dst | Yes |
| move_back | bool | Move from src to dst. It should be True to move back to the original location. | False | Yes |
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

To follow along with this walkthrough, make sure that you have set up your example REDCap according to the instructions above.
Note that all resulting JSONs are reference by their key in `static.json` as individual filenames will change.

### Pull REDCap Data
1. Ensure that you have edited your `read_token.py` file to read in your REDCap API token.
2. In your `config.json`, update your `redcap_url` key to hold your REDCap API URL.
3. Run the following commands:
```python
from main import pipeline_pull_compare_sources
pipeline_pull_compare_sources()
```
    - This will result in two files:
        - `pull_sources_pipeline_redcap_records`: All records pulled from REDCap
        - `pull_sources_pipeline_fix_redcap`: Entries that need to be reviewed and corrected on REDCap. Our sample data should flag the record_id DC265 and DC0212432.

### Walk Sample Data
1. Run the following commands:
```python
from main import pipeline_walk
pipeline_walk()
```
    - This will result in two files:
        - `walk_pipeline_walk`: Files that were found and passed checks.
        - `walk_pipeline_other_walk`: Files containing an unwanted extension or that did not match the filename pattern provided. Our sample data will flag the following files:
            - "sample_data/flac/BL01_06800_20250508_115_remote_bad_extension.flac"
            - "sample_data/m4a/BL00-13234_20241217_112_remote.m4a"
            - "sample_data/mp3/DC0312566.mp3"
            - "sample_data/wav/BL01-06800_20250509_112_in-person.wav",
            - "sample_data/wav/BL01_38126_20250108_in-person.wav"

### Compare filename and REDCap data, flag duplicates
1. In [qc_pipelines.compare_sources_and_duplicates](qc_pipelines.py), update the `record_end_date` in `kwargs` to be your desired end date. For our tests, we used (2025, 4, 30).
2. Run the following commands:
```python
from main import pipeline_compare_sources_and_duplicates
pipeline_compare_sources_and_duplicates()
```
    - This will result in 7 files:
        - `flag_pipeline_passed`: Files that passed all checks.
        - `flag_pipeline_flagged_not_in_date_range_example`: Filename date occurred after the record_end_date.
            - Our sample data will flag DC02-61041_20250507 and BL01-06800_20251015.
        - `flag_pipeline_flagged_no_redcap_entry_example`: Filename id_date did not match those found in the REDCap records.
            - Also see [flagged/no_redcap_entry](flagged/no_redcap_entry/) for an Excel summary.
            - Our sample data will flag DC02-58910_20250101.
        - `flag_pipeline_flagged_tester_id_mismatch_example`: Filenames where the tester_id did not match those found in the REDCap records.
            - Also see [flagged/tester_id_mismatch](flagged/tester_id_mismatch/) for an Excel summary.
            - Our sample data will flag BL01-06800_20250220.
        - `flag_pipeline_duplicates`: Files with same id_date and same contents.
            - Our sample data will flag BL01-04952_20250218.
        - `flag_pipelines_extra_files`: Files with same id_date in the filename.
            - Our sample data will flag BL01-04952_20250218.
        - `flag_pipelines_location_mismatch`: Filenames where the location did not match the location recorded on REDCap.
            - Our sample data will flag BL01-38126_20250108.

### Move and Update the Clean Dataset
1. In [qc_pipelines.move_and_update](qc_pipelines.py), ensure that `move_back` in `kwargs` is set to be `False`.
2. Run the following commands:
```python
from main import pipeline_move_and_update
pipeline_move_and_update()
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