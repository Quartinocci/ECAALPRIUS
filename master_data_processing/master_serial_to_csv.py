import serial
import csv
import time
from datetime import datetime
import threading
import signal
import sys

class ArduinoDataLogger:
    def __init__(self, port='/dev/ttyACM0', baudrate=9600, csv_filename=None, headers=None):
        self.port = port
        self.baudrate = baudrate
        self.data_buffer = []
        self.is_running = False
        self.header_written = False
        
        # Generate filename if not provided
        if csv_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.csv_filename = f"arduino_data_{timestamp}.csv"
        else:
            self.csv_filename = csv_filename

        #TODO test if ok the header non header thing
        self.headers = ['Timestamp'] + headers
            
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
                    if line:
                        # Skip empty lines
                        if not line:
                            continue
                        
                        # Always print to console
                        print(f"Received: {line}")
                        
                        # Skip debug messages - don't save to CSV
                        if line.startswith("DEBUG:"):
                            continue
                        
                        # Parse CSV line (assuming Arduino sends comma-separated values)
                        data_values = line.split(',')
                        
                        # Skip malformed lines
                        if len(data_values) < 1:
                            continue
                            
                        # Add timestamp as first column
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        data_row = [timestamp] + data_values
                        self.data_buffer.append(data_row)
                        
                        # Auto-save every 20 records to prevent data loss
                        if len(self.data_buffer) % 20 == 0:
                            self.save_to_csv()
                            
            except Exception as e:
                print(f"Error reading serial data: {e}")
            
            time.sleep(0.002)  # Small delay to prevent excessive CPU usage
    
    def save_to_csv(self):
        """Save buffered data to CSV file"""
        if not self.data_buffer:
            print("No data to save")
            return
        
        try:
            # Write header only once when file is created
            if not self.header_written:
                with open(self.csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(self.headers)
                    writer.writerows(self.data_buffer)
                self.header_written = True
                print(f"Header and {len(self.data_buffer)} records saved to {self.csv_filename}")
            else:
                # Append data without header
                with open(self.csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerows(self.data_buffer)
                print(f"Appended {len(self.data_buffer)} records to {self.csv_filename}")
            
            self.data_buffer.clear()  # Clear buffer after saving
            
        except Exception as e:
            print(f"Error saving to CSV: {e}")
    
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
        
        # Start serial reading in a separate thread
        serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        serial_thread.start()
        
        print(f"Data logging started. Saving to: {self.csv_filename}")
        print(f"Using headers: {', '.join(self.headers)}")
        print("Press Ctrl+C to stop logging and save data")
        
        return True
    
    def stop_logging(self):
        """Stop logging and save remaining data"""
        print("\nStopping data logger...")
        self.is_running = False
        
        # Save any remaining data
        self.save_to_csv()
        
        # Close serial connection
        if self.serial_connection:
            self.serial_connection.close()
            print("Serial connection closed")
        
        print(f"Final data saved to: {self.csv_filename}")

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    logger.stop_logging()
    sys.exit(0)

if __name__ == "__main__":
    # Configuration - adjust these for your setup
    SERIAL_PORT = '/dev/ttyACM0'  # Change to your Arduino port
    BAUD_RATE = 9600      # Must match Arduino Serial.begin() value

    csv_filename = input("Enter CSV filename (leave empty to skip): ")
    
    # Define custom headers if needed (excluding Timestamp which is automatically added)
    CUSTOM_HEADERS = ['Bench_Level', 'Protocol', 'Run', 'Bus_Voltage', 'Shunt_Voltage', 'Current', 'Power', 'Energy']
    
    # Create logger instance
    logger = ArduinoDataLogger(
        port=SERIAL_PORT, 
        baudrate=BAUD_RATE, 
        csv_filename=csv_filename if csv_filename else None,
        headers=CUSTOM_HEADERS
    )
    
    # Set up graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start logging
    if logger.start_logging():
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.stop_logging()
    else:
        print("Failed to start logging")


