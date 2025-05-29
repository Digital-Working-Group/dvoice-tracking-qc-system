# GRIP Tracking and QC System

## REDCap
### Project Strucure
To buid out your own Qualtity Control System, see `ProjectStructureExample.REDCap.xml` for an example REDCap strucutre. You may import this structure as the base for your own REDCap projects used for GRIP tracking. This project structure has only one form ("Information Sheet") with fields described below:
| Fieldname | Description | Example |
|---|---|---|
| record_id | Record ID for that data. For our testing, we chose the format Cohort Code (two letters and two numbers) and Participant ID (five numbers). All record ids are samples only. | AB0012345 |
| date_dc | The date the data was captured (YYYY-MM-DD) | 2025-05-29 |
| data_loc | The location where the data was collected. | remote |

### REDCap Software Version
REDCap Software - Version 15.2.5 - © 2025 Vanderbilt University
