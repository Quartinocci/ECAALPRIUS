import serial
import csv
import time
from datetime import datetime
import threading
import signal
import sys
import os

class ArduinoDataLogger:
    def __init__(self, port='/dev/ttyACM0', baudrate=115200, csv_filename=None, headers=None):
        self.port = port
        self.baudrate = baudrate
        self.data_buffer = []
        self.is_running = False
        self.header_written = False
        
        # Generate filename if not provided
        if csv_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"arduino_data_{timestamp}.csv"

        # Create folder name based on the CSV filename (without extension)
        folder_name = csv_filename.rsplit('.', 1)[0]
        
        # Create the folder if it doesn't exist
        os.makedirs(folder_name, exist_ok=True)
        print(f"Created folder: {folder_name}")

        # Set full path for CSV file inside the folder
        self.csv_filename = os.path.join(folder_name, csv_filename)
        self.headers = headers if headers else []
        self.serial_connection = None
        
    def connect(self):
        """Establish serial connection to Arduino"""
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"Connected to {self.port} at {self.baudrate} baud")
            time.sleep(1)  # Wait for Arduino to reset
            return True
        except serial.SerialException as e:
            print(f"Error connecting to {self.port}: {e}")
            return False
    
    def read_serial_data(self):
        """Read data from serial port in a separate thread"""
        while self.is_running:
            try:
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    if not line:
                        continue
                    
                    print(f"Received: {line}")
                    
                    # Skip debug messages
                    if line.startswith("DEBUG:"):
                        continue

                    #NOT used, when receiving a message starting with END save everythiong and stop
                    if line.startswith("END:"):
                        os.system('spd-say "Script finished"')
                        print("END signal received - shutting down...")
                        self.stop_logging()
                        sys.exit(0)
                    
                    # Handle POWER data
                    if line.startswith("POWER:"):
                        data_values = line.split(',')[1:]  # Remove "POWER:" part
                        
                        # Validate column count
                        expected_columns = len(self.headers)
                        if expected_columns > 0 and len(data_values) != expected_columns:
                            print(f"Warning: Expected {expected_columns} columns, got {len(data_values)}")
                            continue
                        
                        # Buffer the data
                        self.data_buffer.append(data_values)
                        
                        # Auto-save every 20 records
                        if len(self.data_buffer) % 20 == 0:
                            self.save_to_csv()
                            
            except Exception as e:
                print(f"Error reading serial data: {e}")
            
            time.sleep(0.002)
    
    def save_to_csv(self):
        """Save buffered data to CSV file"""
        if not self.data_buffer:
            return
        
        try:
            mode = 'w' if not self.header_written else 'a'
            with open(self.csv_filename, mode, newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not self.header_written:
                    writer.writerow(self.headers)
                    self.header_written = True
                writer.writerows(self.data_buffer)
            
            print(f"{'Saved' if mode == 'w' else 'Appended'} {len(self.data_buffer)} records to {self.csv_filename}")
            self.data_buffer.clear()
            
        except Exception as e:
            print(f"Error saving data to CSV: {e}")
    
    def start_logging(self):
        """Start the data logging process"""
        print(f"Looking for Arduino on {self.port}...")
        
        # Keep trying to connect until successful
        while not self.connect():
            print("Retrying in 2 seconds... (Press Ctrl+C to quit)")
            try:
                time.sleep(2)
            except KeyboardInterrupt:
                print("\nConnection cancelled by user")
                return False
        
        self.is_running = True
        threading.Thread(target=self.read_serial_data, daemon=True).start()
        
        print(f"Data logging started. Saving to: {self.csv_filename}")
        print(f"Headers: {', '.join(self.headers)}")
        print("Supported formats: POWER:,data | END: (shutdown) | DEBUG: (ignored)")
        print("Press Ctrl+C to stop")
        
        return True
    
    def stop_logging(self):
        """Stop logging and save remaining data"""
        print("\nStopping data logger...")
        self.is_running = False
        self.save_to_csv()
        
        if self.serial_connection:
            self.serial_connection.close()
            print("Serial connection closed")
        
        print(f"Final data saved to: {self.csv_filename}")

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    logger.stop_logging()
    sys.exit(0)

if __name__ == "__main__":
    SERIAL_PORT = '/dev/ttyACM0'
    BAUD_RATE = 115200
    POWER_HEADERS = ['current_runs', 'current_benchmark', 'previoustime', 'current_time', 'currentPower_mW']
    
    csv_filename = input("Enter CSV filename (leave empty for auto-generated): ").strip()
    
    # Ensure filename ends with .csv
    if csv_filename and not csv_filename.endswith('.csv'):
        csv_filename += '.csv'
    
    logger = ArduinoDataLogger(
        port=SERIAL_PORT, 
        baudrate=BAUD_RATE, 
        csv_filename=csv_filename or None,
        headers=POWER_HEADERS
    )
    
    signal.signal(signal.SIGINT, signal_handler)
    
    if logger.start_logging():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.stop_logging()
    else:
        print("Failed to start logging")
