# update_gsheets

## Description

Updating google spreadsheets


## Functions

### __init__
```python
def __init__(self, sheet):
```

### update_data_into_sheet
```python
def update_data_into_sheet(self, sheet_values, sheet_range):
```

#### Description: 
Update data into the specified Google Sheets range


### update_retro_to_sheet
```python
def update_retro_to_sheet(self, new_lines, sheet_range):
```

#### Description: 
Prepare and update retrospective data to the specified Google Sheets range


### update_labels_into_sheet
```python
def update_labels_into_sheet(self, sheet_values, new_lines):
```

#### Description: 
Prepare and update labels data to the Google Sheets LABEL_RANGE


### create_dataset
```python
def create_dataset(self, new_lines, sheet_range):
```

#### Description: 
Create and update a dataset in the specified Google Sheets range


### labeled_unlabeled_diff
```python
def labeled_unlabeled_diff(self, client, spread_range, filter_time):
```

#### Description: 
Calculate and update the difference between labeled and unlabeled services in the specified Google Sheets range


### get_data_from_sheet
```python
def get_data_from_sheet(self, range, sheet_id):
```

#### Description: 
Retrieve data from the Google Sheets LABEL_RANGE


