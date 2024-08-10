import os
from dotenv import load_dotenv
import json  # Importing the JSON module for working with JSON data
import psycopg2  # Importing psycopg2 module for PostgreSQL connection
from psycopg2 import OperationalError  # Importing OperationalError for handling connection issues
import argparse  # Importing the argparse module for parsing command-line arguments
import sys  # Importing the sys module for handling system-specific parameters and functions
import time  # Importing time module for adding delays between retries

from utils.logging import log_progress  # Importing a custom logging function from the utils.logging module

# Load environment variables from .env file
load_dotenv()

def connect_to_postgres():
    """
    Attempts to connect to the PostgreSQL database with retries in case the database is not ready.
    """
    retries = 5  # Number of retries before giving up
    connection = None
    while retries > 0:
        try:
            # Attempt to connect to PostgreSQL
            connection = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST"),
                database=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD")
            )
            print("Connected to PostgreSQL successfully!")
            return connection
        except OperationalError as e:
            # Print the error and retry after a delay
            print(f"Failed to connect to PostgreSQL: {e}")
            retries -= 1
            print(f"Retrying... ({5 - retries}/5)")
            time.sleep(5)  # Wait for 5 seconds before retrying

    raise OperationalError("Could not connect to PostgreSQL after several attempts")


def flatten_order(order):
    """
    Flattens nested order data into a list of dictionaries for easier processing.
    """
    flattened_transactions = []  # Initialize an empty list to store flattened transactions
    try:
        for order_data in order:  # Iterate through each order in the input data
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
                item_code = line['configurations'][0]['itemCode']
                item_count = line['itemCount']
                line_number = line['configurations'][0]['lineNumber']
                item_price = line['configurations'][0]['itemPrice']
                shipping_fee = line['configurations'][0]['shippingFee']
                transaction_line_id = line['transactionLineId']
                product_code = line['item']['productCode']
                merchant_code = line['item']['merchantCode']
                item_name = line['item']['itemName']
                
                # Append the flattened order dictionary to the list of flattened transactions with renamed keys
                flattened_transactions.append({
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

    return flattened_transactions  # Return the list of flattened transactions

def insert_data_to_postgres(data):
    """
    Inserts flattened data into the PostgreSQL database.
    """
    connection = None
    try:
        # Establish the connection to PostgreSQL using the retry mechanism
        connection = connect_to_postgres()
        cursor = connection.cursor()
        
        log_progress("Creating table if not exists...")
        # Create the table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS transactions (
            transactionId VARCHAR(50),
            serviceProvider VARCHAR(50),
            buyerId INTEGER,
            buyerZip VARCHAR(20),
            shippingZip VARCHAR(20),
            purchaseTimestamp TIMESTAMP,
            itemCode VARCHAR(50),
            itemCount INTEGER,
            lineNumber INTEGER,
            itemPrice NUMERIC,
            shippingFee NUMERIC,
            transactionLineId INTEGER,
            productCode VARCHAR(50),
            merchantCode VARCHAR(50),
            itemName VARCHAR(255),
            paymentType VARCHAR(50),
            totalPaid NUMERIC,
            platformCode VARCHAR(50)
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        log_progress("Table creation (if necessary) complete.")

        # Insert data into the table
        insert_query = """
        INSERT INTO transactions (
            transactionId, serviceProvider, buyerId, buyerZip, shippingZip,
            purchaseTimestamp, itemCode, itemCount, lineNumber, itemPrice, 
            shippingFee, transactionLineId, productCode, merchantCode, 
            itemName, paymentType, totalPaid, platformCode
        ) VALUES (
            %(transactionId)s, %(serviceProvider)s, %(buyerId)s, %(buyerZip)s, %(shippingZip)s,
            %(purchaseTimestamp)s, %(itemCode)s, %(itemCount)s, %(lineNumber)s, %(itemPrice)s, 
            %(shippingFee)s, %(transactionLineId)s, %(productCode)s, %(merchantCode)s, 
            %(itemName)s, %(paymentType)s, %(totalPaid)s, %(platformCode)s
        )
        """
        
        log_progress("Inserting data into PostgreSQL...")
        cursor.executemany(insert_query, data)
        connection.commit()

        log_progress(f'Inserted {len(data)} rows into the database.')

    except Exception as error:
        print(f"Failed to insert data into PostgreSQL: {error}", file=sys.stderr)
    finally:
        if connection:
            cursor.close()
            connection.close()

def main(json_file):
    """
    Orchestrates the processing of JSON data into PostgreSQL.
    """
    try:
        log_progress(f'Starting processing JSON file: {json_file}')  # Log the start of processing the JSON file
        with open(json_file) as f:  # Open the JSON file
            data = json.load(f)  # Load its contents into memory
        
        flattened_data = flatten_order(data)  # Flatten the JSON data
        insert_data_to_postgres(flattened_data)  # Insert the flattened data into PostgreSQL
        log_progress('Data insertion to PostgreSQL completed.')  # Log the completion of data insertion

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
    parser = argparse.ArgumentParser(description="Process sales JSON data into PostgreSQL.")  # Create an argument parser
    parser.add_argument("--json", help="Path to JSON file", required=True)  # Add argument for JSON file path
    args = parser.parse_args()  # Parse the command-line arguments
    
    main(args.json)  # Call the main function with the provided JSON file path
