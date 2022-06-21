"""
Template Component main class.

"""
import csv
import logging

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

# configuration variables
KEY_API_TOKEN = '#api_token'
KEY_PARAM_PRINT_LINES = 'print_rows'

# list of mandatory parameters => if some is missing,
# component will fail with readable message on initialization.
REQUIRED_PARAMETERS = [KEY_PARAM_PRINT_LINES]
REQUIRED_IMAGE_PARS = []


class Component(ComponentBase):
    """
        Extends base class for general Python components. Initializes the CommonInterface
        and performs configuration validation.

        For easier debugging the data folder is picked up by default from `../data` path,
        relative to working directory.

        If `debug` parameter is present in the `config.json`, the default logger is set to verbose DEBUG mode.
    """

    def __init__(self):
        super().__init__()

    def run(self):
        """
        Main execution code
        """
        print('Running...')
        # check for missing configuration parameters
        self.validate_configuration_parameters(REQUIRED_PARAMETERS)
        self.validate_image_parameters(REQUIRED_IMAGE_PARS)
        params = self.configuration.parameters

        # Load input table
        in_table = self.get_input_table_definition_by_name('input.csv')
        in_table_path = in_table.full_path
        logging.info(in_table_path)

        # Create output table (Tabledefinition - just metadata)
        out_table = self.create_out_table_definition('output.csv')
        out_table_path = out_table.full_path
        logging.info(out_table_path)

        with open(in_table_path, 'r') as input, open(out_table_path, mode='w+', newline='') as out:
            reader = csv.DictReader(input)
            new_columns = reader.fieldnames
            # append row number col
            new_columns.append('row_number')
            writer = csv.DictWriter(out, fieldnames=new_columns, lineterminator='\n', delimiter=',')
            writer.writeheader()
            for index, l in enumerate(reader):
                # print line
                if params.get(KEY_PARAM_PRINT_LINES):
                    print(f'Printing line {index}: {l}')
                # add row number
                l['row_number'] = index
                writer.writerow(l)

        # Save table manifest (output.csv.manifest) from the tabledefinition
        self.write_manifest(out_table)

        # Write new state - will be available next run
        self.write_state_file({"some_state_parameter": "value"})


"""
        Main entrypoint
"""
if __name__ == "__main__":
    try:
        comp = Component()
        # this triggers the run method by default and is controlled by the configuration.action parameter
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
