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
