# build_bigquery

## Description

Building Dataframes after requesting from BigQuery


## Functions

### get_report
```python
def get_report(cdf, months, *grouper):
```

#### Description: 
Build custom  full retrospective report


### __init__
```python
def __init__(self, client):
```

### build_dataframe
```python
def build_dataframe(self, data):
```

#### Description: 
Build dataframe from bigquery row data


### get_data
```python
def get_data(self, query_string):
```

#### Description: 
Execute a BigQuery query and return the result as a DataFrame


### get_retro_data
```python
def get_retro_data(self, year_month):
```

#### Description: 
Retrieve retrospective data for a specific month


### get_retro_cost
```python
def get_retro_cost(self, month):
```

#### Description: 
Retrieve retrospective cost data for a specific month


### get_cost_by_owner
```python
def get_cost_by_owner(self, time_filter):
```

#### Description: 
Query to get cost by owner


### get_cost_by_env
```python
def get_cost_by_env(self, time_filter):
```

#### Description: 
Query to get cost by env


### get_cost_by_service
```python
def get_cost_by_service(self, time_filter):
```

#### Description: 
Query to get cost by service


### get_cost_by_labeled_service
```python
def get_cost_by_labeled_service(self, time_filter):
```

#### Description: 
Query to get cost by labeled service


### get_labels_env
```python
def get_labels_env(self):
```

#### Description: 
Query to get the values of labels env and used_by


