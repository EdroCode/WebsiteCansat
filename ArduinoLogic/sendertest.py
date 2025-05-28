import serial
import time

SERIAL_PORT = 'COM3'
BAUD_RATE = 9600

# Message to send (24 comma-separated values)
test_message = "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,25.5,0,0,0,0,0,0,0,0"

def main():
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as ser:
            while True:
                print(f"Opened serial port {SERIAL_PORT}")
                time.sleep(2)  # Give Arduino time to reset after opening port
                
                ser.write((test_message + "\n").encode('utf-8'))
                print("Message sent to Arduino:")
                print(test_message)
                
                # Optional: Read response if any
                time.sleep(1)
                while ser.in_waiting:
                    line = ser.readline().decode('utf-8').strip()
                    print(f"Arduino: {line}")
                time.sleep(5)
    
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("Interrupted by user.")

if __name__ == "__main__":
    main()
