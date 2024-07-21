# Building Dataframes after requesting from BigQuery
import pandas as pd
from src.utils import *
import os
from src.constants import  BILLING_DATASET

# Build custom  full retrospective report
def get_report(cdf, months, *grouper):
    if isinstance(months, str):
        months = [months]
    return (cdf.groupby([pd.Grouper(key='usage_time', freq='1M'), *grouper])
        .cost.sum()
        .reset_index()
        .assign(month=lambda df:df['usage_time'].dt.strftime('%Y-%m'))
        .pipe(lambda df: df[df.month.isin(months)])
        .drop('usage_time', axis='columns')
        .pivot(columns='month', index=grouper, values='cost')
        .fillna(0)
        )

class BigQuery:
    def __init__(self, client):
        self.client = client

# Build dataframe from bigquery row data
    def build_dataframe(self, data):
        try:
            print_loading("Creating DataFrame...")
            df = pd.DataFrame(map(dict, data))
            print_success("DataFrame creation completed successfully.")
        except Exception as e:
            print_error(f"DataFrame creation failed with the following error: {str(e)}")
            df = pd.DataFrame()

        return df

# Execute a BigQuery query and return the result as a DataFrame
    def get_data(self, query_string, dump=None):
        wait = True
        response = self.client.query(query_string)
        while wait:
            if response.running():
                loading('waiting query...')
            else:
                wait = False
        data = response.result()
        if dump:
            return data
        else:
            return self.build_dataframe(data)

# Retrieve retrospective data for a specific month
    def get_retro_data(self, year_month):
        query = f"""
        SELECT 
            usage_end_time AS usage_time,
            coalesce(labels.value,'*') AS env,
            coalesce(env_info.owner,'?') AS env_owner,
            coalesce(env_info.customer,'?') AS env_customer,
            coalesce(env_info.Purpose,'?') AS env_purpose,
            billing.sku.description as sku,
            coalesce(cat.category, 'UNKNOWN') AS category,
            SUM(cost) as cost
        FROM {BILLING_DATASET} as billing
        LEFT JOIN UNNEST(labels) as labels
        ON labels.key = "env"
        LEFT JOIN `opensee-ci.billing_report.env_owner_info` as env_info
        ON coalesce(labels.value, '*') = env_info.env
        LEFT JOIN `opensee-ci.billing_report.sku_cat` as cat
        ON billing.sku.description = cat.sku
        WHERE
            DATE(_PARTITIONTIME) >= "{year_month}-01"  and cost>0.0
        GROUP BY
            usage_end_time, env, category, env_owner, env_customer, env_purpose, sku
        ORDER BY
            usage_end_time  
            """
        return self.get_data(query)

# Retrieve retrospective cost data for a specific month
    def get_retro_cost(self, month):
        if not os.path.exists(f'data_{month}.csv'):
            months = format_month(month)
            retro = self.get_retro_data(months["bpm"])
            cdf = retro[retro.category != 'Tax']
            cdf.to_csv(f'data_{month}.csv', sep=',', index=False, encoding='utf-8')
        else:
            print(f'Retro {month} is already loaded')
            cdf = pd.read_csv(f'data_{month}.csv')
            cdf['usage_time'] = pd.to_datetime(cdf['usage_time'])
        return cdf

# Query to get cost by owner
    def get_cost_by_owner(self, time_filter):
        query = f"""
        SELECT l.value as Owner,sum(cost) AS cost
        FROM {BILLING_DATASET}, UNNEST(labels) as l
        where l.key = "used_by" and {time_filter} And cost > 0
        GROUP BY Owner
        ORDER BY cost DESC
            """
        return self.get_data(query)

# Query to get cost by env
    def get_cost_by_env(self, time_filter):
        query = f"""
        SELECT l.value as env, COALESCE(o.value, '?') as owner, sum(cost) AS cost
        FROM {BILLING_DATASET}, UNNEST(labels) as l  LEFT JOIN UNNEST(labels) as o ON o.key = "used_by"
        where l.key = "env" and {time_filter} And cost > 0
        GROUP BY env, owner
        ORDER BY cost DESC
            """
        return self.get_data(query)

# Query to get cost by service
    def get_cost_by_service(self, time_filter):
        query = f"""
        SELECT service.description AS metric, sum(cost) AS cost
        FROM {BILLING_DATASET}
         WHERE {time_filter} And cost > 0 AND service.description != "Invoice" 
        GROUP BY metric
        ORDER BY cost DESC
            """
        return self.get_data(query)

# Query to get cost by labeled service
    def get_cost_by_labeled_service(self, time_filter):
        query = f"""
        SELECT service.description AS metric, sum(cost) AS cost
        FROM {BILLING_DATASET}, UNNEST(labels) as l
         WHERE {time_filter} And cost > 0 AND service.description != "Invoice" AND l.key = "env"
        GROUP BY metric
        ORDER BY cost DESC
            """
        return self.get_data(query)

# Query to get the values of labels env and used_by
    def get_labels_env(self):
        query = f"""
        SELECT 
            e.value AS env,
            o.value AS owner
        FROM {BILLING_DATASET}, UNNEST(labels) as e JOIN UNNEST(labels) as o
        WHERE
           e.key = "env" AND o.key = "used_by" AND cost > 0
        GROUP BY
            env, owner
            """
        return self.get_data(query)
    
# Query to dump billing data
    def dump_billing_dataset(self, date_range):
        query = f"""
        SELECT
          billing_account_id,
          resource.name as resource_name,
          service.description AS service_description,
          sku.description AS sku_description,
          usage_start_time,
          usage_end_time,
          project.name AS project_name,
          label_env.value AS env,
          label_client.value AS client,
          label_purpose.value AS purpose,
          label_env.value AS used_by,
          location.location AS location,
          location.region AS region,
          export_time,
          cost,
          currency,
          usage.amount AS usage_amount,
          usage.unit AS usage_unit,
          invoice.month AS invoice_month,
          seller_name
        FROM
            {BILLING_DATASET}  AS billing
        LEFT JOIN
            UNNEST(labels) AS label_env
        ON
            label_env.key = "env"
        LEFT JOIN
            UNNEST(labels) AS label_client
        ON
            label_client.key = "client"
        LEFT JOIN
            UNNEST(labels) AS label_purpose
        ON
            label_purpose.key = "purpose"
        LEFT JOIN
            UNNEST(labels) AS label_used_by
        ON
            label_used_by.key = "used_by"
        WHERE
            export_time > TIMESTAMP("{date_range[0]}") and export_time <= TIMESTAMP("{date_range[1]}")
        """
        return self.get_data(query, dump=True)    