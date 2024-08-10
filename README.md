## eCommerce Data Modeling 

A data modeling project utilizing PostgreSQL and pgAdmin, running on Docker containers.

Disclaimer: The dataset used in this project is inspired by real-world business data; however, it is entirely fictional. It was generated using a combination of ChatGPT's capabilities and additional inputs from myself and my experiences. Any resemblance to actual data is purely coincidental.

### Add a Docker Compose Setup with PostgreSQL and pgAdmin4

#### Steps:

1. Create a docker-compose.yml file under the root directory
ecommerce-data-modeling > docker-compose.yml
  ```yml
  version: "3.8"
  services:
    db:
      container_name: postgres_container
      image: postgres
      restart: always
      environment:
        POSTGRES_USER: root
        POSTGRES_PASSWORD: root
        POSTGRES_DB: test_db
      ports:
        - "5432:5432"
    pgadmin:
      container_name: pgadmin4_container
      image: dpage/pgadmin4
      restart: always
      environment:
        PGADMIN_DEFAULT_EMAIL: admin@admin.com
        PGADMIN_DEFAULT_PASSWORD: root
      ports:
        - "5050:80"
  ```

2. Install [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/), and follow installation procedure from the deocumentation.

3. Open Docker Desktop

4. On the terminal, run:
  ```
  docker pull postgres
  docker-compose up
  ```

5. On your browser of choice, enter localhost:5050. You will the the pgAdmin UI

6. Enter the credentials set on the docker-compose.yml
  ```
  email: admin@admin.com
  password: root
  ```

7. Click login

8. Open a new terminal and run
  ```
  docker container ls
  ```

9. Copy postgres container ID and run
  ```
  docker inspect <container-id>
  ```

10. Copy the IPAddress. For example: 172.18.0.2

11. On pgAdmin, click Add New Server

12. Add name. For example: ps_db

13. Go to connection tab and 
  a. Add the IPAdress. For example: 172.18.0.2
  b. Set username to root
  c. Enter the password: root
  d. Save

14. Under servers, you'll see postgres and test_db databases
  Note: test_db is the database set up in the .yml file

### Transform JSON Data to CSV Using Python
1. Create utils folder on the root directory

2. Under the utils folder, add a file named as __init__.py

3. Under the utils folder, add a file named as logging.py and add the following script to create a logging module
  ```python
  # Import the datetime class from the datetime package to handle date and time-related functions
  from datetime import datetime 

  # Define the path for the log file where the logging information will be stored
  log_file = "logs/pipeline_log.txt"

  def log_progress(message):
    """
    Logs a message with a timestamp to the specified log file.
    
    This function appends a message, along with the current timestamp, to a log file. 
    It is useful for tracking the progress and stages of code execution, particularly 
    in data pipelines or long-running processes.

    Parameters:
    message (str): The message to be logged. This could include details about the 
                   current stage of execution, any errors encountered, or other 
                   relevant information.

    Returns:
    None: This function does not return anything.
    """
    
    # Define the format for the timestamp, including year, month (abbreviated), day, hour, minute, and second
    timestamp_format = '%Y-%b-%d-%H:%M:%S'  
    
    # Get the current time as a datetime object
    now = datetime.now()  
    
    # Convert the datetime object to a string in the specified format
    timestamp = now.strftime(timestamp_format)  
    
    # Open the log file in append mode so that each new message is added to the end of the file
    with open(log_file, "a") as f:  
        # Write the timestamp and message to the log file, followed by a newline character
        f.write(f"{timestamp}, {message}\n")  
  ```

4. Under the root directory, create a folder called logs

5. Under the root directory, create a file named as json_to_csv.py
```python
  import json  # Importing the JSON module for working with JSON data
  import csv  # Importing the CSV module for working with CSV files
  import argparse  # Importing the argparse module for parsing command-line arguments
  import sys  # Importing the sys module for handling system-specific parameters and functions

  from utils.logging import log_progress  # Importing a custom logging function from the utils.logging module

  def flatten_order(order):
      """
      Flattens nested order data into a list of dictionaries for easier processing.

      This function extracts and organizes data from complex, nested JSON order structures into a flat 
      dictionary format. Each order is represented by one or more dictionaries, corresponding to each line 
      item in the order. These dictionaries are then stored in a list for further processing, such as writing 
      to a CSV file.

      Parameters:
      order (list): A list of dictionaries, where each dictionary represents an order in nested JSON format.

      Returns:
      list: A list of dictionaries where each dictionary represents a single line item from an order, with 
      relevant details flattened.
      """
      flattened_orders = []  # Initialize an empty list to store flattened orders
      try:
          for order_data in order:  # Iterate through each order in the input data
              # Extracting various fields from the nested order data and assigning them to variables
              transaction_id = order_data['transaction']['transactionId']
              service_provider = order_data['transaction']['serviceProvider']
              buyer_id = order_data['transaction']['details']['buyer']['buyerId']
              buyer_zip = order_data['transaction']['details']['buyer']['address']['buyerZip']
              shipping_zip = order_data['transaction']['details']['shipping']['shippingZip']
              purchase_timestamp = order_data['transaction']['details']['purchaseTimestamp']
              payment_type = order_data['transaction']['details']['payment']['paymentType']
              total_paid = order_data['transaction']['details']['payment']['totalPaid']
              platform_code = order_data['transaction']['details']['platform']['platformCode']
              
              for line in order_data['transaction']['details']['items']:  # Iterate through each line item within the order
                  # Extract line item details and add them to a dictionary representing the flattened order
                  item_code = line['configurations'][0]['itemCode']
                  item_count = line['itemCount']
                  line_number = line['configurations'][0]['lineNumber']
                  item_price = line['configurations'][0]['itemPrice']
                  shipping_fee = line['configurations'][0]['shippingFee']
                  transaction_line_id = line['transactionLineId']
                  product_code = line['item']['productCode']
                  merchant_code = line['item']['merchantCode']
                  item_name = line['item']['itemName']
                  
                  # Append the flattened order dictionary to the list of flattened orders with renamed keys
                  flattened_orders.append({
                      'transactionId': transaction_id,
                      'serviceProvider': service_provider,
                      'buyerId': buyer_id,
                      'buyerZip': buyer_zip,
                      'shippingZip': shipping_zip,
                      'purchaseTimestamp': purchase_timestamp,
                      'itemCode': item_code,
                      'itemCount': item_count,
                      'lineNumber': line_number,
                      'itemPrice': item_price,
                      'shippingFee': shipping_fee,
                      'transactionLineId': transaction_line_id,
                      'productCode': product_code,
                      'merchantCode': merchant_code,
                      'itemName': item_name,
                      'paymentType': payment_type,
                      'totalPaid': total_paid,
                      'platformCode': platform_code
                  })
                  
                  log_progress(f'Processed line: {transaction_line_id} from transaction: {transaction_id}')  # Log the progress of processing each line item

      except KeyError as e:
          print(f"KeyError occurred: {e}", file=sys.stderr)  # Print error message to standard error stream
          sys.exit(1)  # Exit the program with non-zero status indicating error

      return flattened_orders  # Return the list of flattened orders

  def write_to_csv(data, filename):
      """
      Writes flattened data to a CSV file.

      This function takes a list of dictionaries (typically the output of flatten_order) and writes 
      it to a CSV file. Each dictionary in the list represents a row in the CSV file, and the keys 
      of the dictionary correspond to the column headers.

      Parameters:
      data (list): A list of dictionaries to be written to the CSV file. Each dictionary represents 
                  a single row in the CSV.
      filename (str): The name of the file where the data will be written. If the file does not exist, 
                      it will be created.

      Returns:
      None: This function does not return anything.
      """
      try:
          with open(filename, 'w', newline='') as csvfile:  # Open a CSV file in write mode
              fieldnames = ['transactionId', 'serviceProvider', 'buyerId', 'buyerZip', 'shippingZip',
                          'purchaseTimestamp', 'itemCode', 'itemCount', 'lineNumber', 'itemPrice', 'shippingFee',
                          'transactionLineId', 'productCode', 'merchantCode', 'itemName', 'paymentType', 'totalPaid',
                          'platformCode']  # Define fieldnames for the CSV file with the renamed keys
              writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  # Create a CSV writer object
              writer.writeheader()  # Write the header row with field names
              writer.writerows(data)  # Write each dictionary in the data list as a row in the CSV file
      
      except IOError as e:
          print(f"IOError occurred: {e}", file=sys.stderr)  # Print error message to standard error stream
          sys.exit(1)  # Exit the program with non-zero status indicating error

  def main(json_file, csv_file):
      """
      Orchestrates the processing of JSON data into a CSV file.

      This function serves as the entry point for processing JSON order data. It coordinates the reading 
      of JSON data, flattening the data structure, and writing the flattened data to a CSV file.

      Parameters:
      json_file (str): The path to the JSON file containing the order data.
      csv_file (str): The path to the CSV file where the flattened data will be written.

      Returns:
      None: This function does not return anything.
      """
      try:
          log_progress(f'Starting processing JSON file: {json_file}')  # Log the start of processing the JSON file
          with open(json_file) as f:  # Open the JSON file
              data = json.load(f)  # Load its contents into memory
          
          flattened_data = flatten_order(data)  # Flatten the JSON data
          log_progress(f'Writing to CSV file: {csv_file}')  # Log the start of writing to the CSV file
          write_to_csv(flattened_data, csv_file)  # Write the flattened data to a CSV file
          log_progress('CSV file generation completed.')  # Log the completion of CSV file generation

      except FileNotFoundError as e:
          print(f"FileNotFoundError occurred: {e}", file=sys.stderr)  # Print error message to standard error stream
          sys.exit(1)  # Exit the program with non-zero status indicating error
      except json.JSONDecodeError as e:
          print(f"JSONDecodeError occurred: {e}", file=sys.stderr)  # Print error message to standard error stream
          sys.exit(1)
      except Exception as e:
          print(f"An unexpected error occurred: {e}", file=sys.stderr)  # Print error message to standard error stream
          sys.exit(1)
          
  if __name__ == "__main__":
      parser = argparse.ArgumentParser(description="Process sales JSON data into CSV.")  # Create an argument parser
      parser.add_argument("--json", help="Path to JSON file", required=True)  # Add argument for JSON file path
      parser.add_argument("--csv", help="Path to CSV file", required=True)  # Add argument for CSV file path
      args = parser.parse_args()  # Parse the command-line arguments
      
      main(args.json, args.csv)  # Call the main function with the provided JSON and CSV file paths


```
6. Under the root directory, create a folder named as processed-data to store the output transformed data from the Python script

7. Run the following command on the terminal
  ```terminal
    python json_to_csv.py --json raw-data/tindera.json --csv processed-data/tindera_output.csv
  ```