# Digital Voice Tracking and QC System

Instructions for using REDCap as a source instead of an input CSV. General instructions can be found in the main [README.md](README.md).

## Sample QC Walkthrough

### REDCap Setup
1. Select **New Project**.
2. For the **Project creation option** select *Upload a REDCap project XML file (CDISC ODM format)*. If you would like to use our structure but create your own sample data, use [ProjectStructureExample.REDCAP.xml](templates/ProjectStructureExample.REDCap.xml) or upload with our sample data using [ProjectStructure_with_data.xml](templates/ProjectStructure_with_data.xml).
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

### Pull Records
Set `source='redcap'` and the pipeline will read and validate records from a specified REDCap Project. By default, the source will be 'csv'.

#### Pull Records: Source from REDCap
```python
import qc_pipelines as qcp
from read_token import read_token

if __name__ == '__main__':
    PULL_RECORDS_KW = rc_kwargs = {'fields_list': ['record_id',
                                                    'date_dc',
                                                    'tester_id',
                                                    'data_loc',
                                                    'information_sheet_complete'],
                                    'token': read_token,
                                    'redcap_url': gld.get_root_fp('redcap_url')}
    qcp.pull_records(source='redcap', **PULL_RECORDS_KW)
```
- This will result in three files:
    - `records_pipeline_redcap_records`: All records read from REDCap.
    - `records_pipeline_validated_records`: All records read from REDCap that passed the validation check.
    - `records_pipeline_fix_record`: Records that need to be reviewed and corrected.
    - Our sample data result in the flagging of:
        - missing_fields: DC02-12432_20241123
        - invalid_id: DC265
- Change `read_token` to read the text file that stores your REDCap token.
    - You may modify [templates/read_token_template.py](templates/read_token_template.py).
#### Keyword Arguments for pull_records()

**pull_redcap**
| variable name | type(s) | description | default value | optional |
|---|---|---|---|---|
| fields_list | list | Fields to pull from REDCap. | [] | No |
| token | func | Method that gets token. | No default | No |
| redcap_url | str| REDCap API URL for your project. | No | No |
| ext | str | Resulting JSON filename extension. | 'redcap_records' | Yes |
