# Updating google spreadsheets
from src.constants import (
    RETRO_PURPOSE_RANGE,
    RETRO_SAAS_RANGE,
    BILLING_SPREADSHEET_ID,
    LABEL_SPREADSHEET_ID,
    LABEL_RANGE,
    OWNER_RANGE,
    ENV_RANGE,
)
from src.utils import *
from bigquery.build_bigquery import BigQuery

class GSheets:
    def __init__(self, sheet):
        self.sheet = sheet

# Update data into the specified Google Sheets range
    def update_data_into_sheet(self, sheet_values, sheet_range):
        if sheet_range == LABEL_RANGE:
            sheet_id = LABEL_SPREADSHEET_ID
        else:
            sheet_id = BILLING_SPREADSHEET_ID

        # Update the spreadsheet with the new lines
        request = self.sheet.values().update(
            spreadsheetId=sheet_id,
            range=sheet_range,
            valueInputOption='USER_ENTERED',
            body={'values': sheet_values}
        )
        response = request.execute()

        if response.get('updatedCells') > 0:
            print_success('Lines added successfully.')
        else:
            print_success('No lines were added.')

# Prepare and update retrospective data to the specified Google Sheets range
    def update_retro_to_sheet(self, new_lines, sheet_range):
        sheet_values = []
        row_names = []
        column_names = ['Month']

        if sheet_range == RETRO_PURPOSE_RANGE:
            row_names = ['Owner', 'Purpose']
            column_names.append('')
        elif sheet_range == RETRO_SAAS_RANGE:
            row_names = ['Owner', 'Customer']
            column_names.append('')

        for col in new_lines.columns:
            column_names.append(col)

        sheet_values.append(column_names)
        sheet_values.append(row_names)

        if sheet_range == RETRO_PURPOSE_RANGE or sheet_range == RETRO_SAAS_RANGE:
            for n, line in new_lines.iterrows():
                new = [n[0], n[1], line.iloc[0], line.iloc[1], line.iloc[2]]
                sheet_values.append(new)
        else:
            for n, line in new_lines.iterrows():
                new = [n, line.iloc[0], line.iloc[1], line.iloc[2]]
                sheet_values.append(new)

        return self.update_data_into_sheet(sheet_values, sheet_range)

# Prepare and update labels data to the Google Sheets LABEL_RANGE
    def update_labels_into_sheet(self, sheet_values, new_lines):
        for _, line in new_lines.iterrows():
            if line.iloc[0] in str(sheet_values):
                print_loading('Line already exists in the spreadsheet.')
            else:
                new = [line.iloc[0], line.iloc[1]]
                sheet_values.append(new)

        return self.update_data_into_sheet(sheet_values, LABEL_RANGE)

# Create and update a dataset in the specified Google Sheets range
    def create_dataset(self, new_lines, sheet_range):
        if sheet_range == OWNER_RANGE:
            sheet_values = [['Owner', 'Cost']]
            for _, line in new_lines.iterrows():
                new = [line.iloc[0], line.iloc[1]]
                sheet_values.append(new)
        elif sheet_range == ENV_RANGE:
            sheet_values = [['Env','Owner','Cost']]
            for _, line in new_lines.iterrows():
                new = [line.iloc[0], line.iloc[1], line.iloc[2]]
                sheet_values.append(new)
        else:
            sheet_values = []

        return self.update_data_into_sheet(sheet_values, sheet_range)

# Calculate and update the difference between labeled and unlabeled services in the specified Google Sheets range
    def labeled_unlabeled_diff(self, client, spread_range, filter_time):
        bq = BigQuery(client)
        services = bq.get_cost_by_service(filter_time)
        labeled_services = bq.get_cost_by_labeled_service(filter_time)
        sheet_values = [['Service', 'Cost', 'Labeled_Cost', 'Diff']]

        for _, line in services.iterrows():
            new = [line.iloc[0], line.iloc[1]]
            sheet_values.append(new)

        for services in sheet_values:
            for _, line in labeled_services.iterrows():
                if services[0] == line.iloc[0]:
                    services.append(line.iloc[1])
                
        for service in sheet_values:
            if len(service) == 3:
                service.append(f'=Minus(I{sheet_values.index(service) + 1};J{sheet_values.index(service) + 1})')
            elif len(service) == 2:
                service.append('')
                service.append(f'=Minus(I{sheet_values.index(service) + 1};J{sheet_values.index(service) + 1})')

        return self.update_data_into_sheet(sheet_values, spread_range)

# Retrieve data from the Google Sheets LABEL_RANGE
    def get_data_from_sheet(self, range, sheet_id):
        result_input = self.sheet.values().get(spreadsheetId=sheet_id,
                                               range=range).execute()
        return result_input.get('values', [])