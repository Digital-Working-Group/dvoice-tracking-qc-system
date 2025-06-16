# GRIP Tracking and QC System

This repository contains an outline to set up qc_pipelines and walks through an example qc run on an example REDCap with fictitious participant data.

| Table of Contents |
|---|
| Introduction |
| REDCap Details |
| Repository Contents |
| Installation and Setup |
| QC Steps |
| Running a QC: Example |

# Introduction
See (main.py)[main_template.py] and (qc_pipelines.py)[qc_pipelines.py]. These scripts were developed using Python 1.13.1, but have been tested with (CODY + JULIA ADD).

# REDCap Details
## Project Strucure
To buid out your own Qualtity Control System, see `ProjectStructureExample.REDCap.xml` for an example REDCap strucutre. You may import this structure as the base for your own REDCap projects used for GRIP tracking. This project structure has only one form ("Information Sheet") with fields described below:
| Fieldname | Description | Example |
|---|---|---|
| record_id | Record ID for that data. For our testing, we chose the format Cohort Code (two letters and two numbers) and Participant ID (five numbers). All record ids are samples only. | AB0012345 |
| date_dc | The date the data was captured (YYYY-MM-DD) | 2025-05-29 |
| data_loc | The location where the data was collected. | remote |

## REDCap Software Version
REDCap Software - Version 15.2.5 - © 2025 Vanderbilt University

# Repository Contents
This repository contains scripts to build and customize pipelines as well as sample data to follow along with the example presented below. 
To familiarize yourself with this repository, consider exploring:
    - (qc_pipelines.py)[qc_pipelines.py]: combines scripts by inputting them as nodes to pipelines to build out the strucutre of the qc
    - (stream.py)[stream.py]: holds the Pipeline and Node class structures
    - (logger.py)[logger.py]: handles the saving and logging of pipeline results
    - (redcap.py)[redcap.py]: handles pulling and validating REDCap records
    - (walk.py)[walk.py]: walk functions to collect files
    - (compare_redcap.py)[compare_redcap.py]: functions to compare filename information to REDCap field data
    - (write_flagged_excel.py)[write_flagged_excel.py]: writes excels for manual review
    - (duplicates.py)[duplicates.py]: functions to check for duplicates or too many file occurences
    - (destination.py)[destination.py]: functions to define destination of files that passed all checks
    - (move.py)[move.py]: functions to move files
    - (clean_dataset.py)[clean_dataset.py]: functions to compare to and update the clean dataset of all files that have passed the QC

To follow along with the example, use the files found in (redcap_example/)[redcap_example] to set up your REDCap Project.

# Installation and Setup
## Script setup
Install the requirements needed to run these scripts:
```sh
pip install -r py3-13-1_requirements.txt
```

See (templates)[templates/] for the template files you should copy. Copy each one into your `qc_system` folder and rename by removing *template* from the filename. Fill in any filepaths, tokens, or URLs needed.

## REDCap Setup
Add here 

# QC Steps
### Prepare comparison sources
Our example only compares to REDCap, but you may wish to add additional nodes to compare with other data sources.
1. Run `pull_comparison_sources()` from `main()`
    - This pulls data from REDCap and reformats to be keyed by id_date.

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
2. Check the *walk_pipeline_walk* and *walk_pipeline_other_walk* JSON files to resolve any issues. Issues and resolutions include:
    - Wrong extension type: Move file to the appropriate folder.
    - No match: Filename did not match the regex. Modify the filename to fit the expected pattern.
    - Invalid date: Verify the date with your team.
3. Rerun the script until the failures have been resolved. 
    - You may want to move on to the next step before fixing all of these errors if you are waiting on input from team members.
#### KWARGS
| variable name | type(s) | description | default value | optional |
|---|---|---|---|---|
| pattern_list | list | Tuples of regex pattern and indices. | None | Yes |
| make_kv | func | Defines key-value pairs for walk data. | default_make_kv | Yes |
| ignore_list | list | Files or folders to ignore in walk. | [] | Yes |
| roots | list | Filepaths to crawl. | No default | No |
| keep_exts | tuple | File extensions to look for. | No default | No |
| walk_kwargs | dict | Any additional walk kwargs. | {} | Yes |

### Compare sources and duplicates
This step filters based on some example critera to ensure that the filenames match the data recorded on REDCap and that there are no extra or duplicate files. The specific steps used in this example inclue:
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

# Running a QC: Example