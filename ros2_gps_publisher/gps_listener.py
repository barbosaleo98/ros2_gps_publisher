import socket
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point  # Import Point for GPS coordinates

# Define the UDP IP and port
UDP_IP = "0.0.0.0"  # Listen on all interfaces
UDP_PORT = 5000

class GPSPublisher(Node):
    def __init__(self):
        super().__init__('ros2_gps_publisher')
        self.publisher_ = self.create_publisher(Point, 'gps_coordinates', 10)  # Change the message type
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP, UDP_PORT))
        self.get_logger().info(f"Listening for GPS data on UDP port {UDP_PORT}...")

    def convert_to_degrees(self, value, direction):
        degrees = int(value) // 100
        minutes = value - (degrees * 100)
        decimal_degrees = degrees + (minutes / 60)
        if direction in ['S', 'W']:
            decimal_degrees = -decimal_degrees
        return decimal_degrees

    def listen_for_gps_data(self):
        while rclpy.ok():
            data, _ = self.sock.recvfrom(1024)  # Buffer size is 1024 bytes
            gpspipe_data = data.decode('utf-8').strip()  # Decode the byte data

            self.get_logger().debug(f"Received data from gpspipe: {gpspipe_data}")

            nmea_sentences = gpspipe_data.split('$')

            for sentence in nmea_sentences:

                # Match GPRMC sentence
                if "GPRMC" in sentence:
                    self.get_logger().debug(f"Received GPRMC sentence: {sentence}")

                    # Split the sentence into components
                    parts = sentence.split(',')
                    if len(parts) > 2 and parts[2] == 'A':  # Check if the data is valid
                        try:
                            latitude = float(parts[3])
                            lat_direction = parts[4]
                            longitude = float(parts[5])
                            lon_direction = parts[6]

                            # Convert to degrees
                            lat_decimal = self.convert_to_degrees(latitude, lat_direction)
                            lon_decimal = self.convert_to_degrees(longitude, lon_direction)

                            # Convert to microdegrees (optional, if needed)
                            lat_micro = lat_decimal #* 1_000_000
                            lon_micro = lon_decimal #* 1_000_000

                            # Create a Point message for latitude and longitude
                            gps_coordinates = Point()
                            gps_coordinates.x = lat_micro  # Latitude
                            gps_coordinates.y = lon_micro  # Longitude
                            gps_coordinates.z = 0.0  # You can set this to 0 or leave it as per your requirement

                            # Publish latitude and longitude in microdegrees
                            self.publisher_.publish(gps_coordinates)
                            self.get_logger().info(f"Published: Latitude (microdegrees): {lat_micro}, Longitude (microdegrees): {lon_micro}")

                        except ValueError:
                            self.get_logger().error("Invalid latitude or longitude value in GPRMC sentence.")

                # Match GPGGA sentence
                if "GPGGA" in sentence:

                    self.get_logger().debug(f"Received GPGGA sentence: {sentence}")

                    # Split the sentence into components
                    parts = sentence.split(',')
                    if len(parts) > 4:  # Ensure we have enough parts
                        try:
                            if parts[2]:  # Check if latitude is provided
                                latitude = float(parts[2])
                                lat_direction = parts[3]
                                if parts[4]:  # Check if longitude is provided
                                    longitude = float(parts[4])
                                    lon_direction = parts[5]
                                    # Convert to degrees
                                    lat_decimal = self.convert_to_degrees(latitude, lat_direction)
                                    lon_decimal = self.convert_to_degrees(longitude, lon_direction)
                                    #print(lat_decimal, lon_decimal)
                                    self.get_logger().info(f"Published: Latitude (microdegrees): {lat_decimal}, Longitude (microdegrees): {lon_decimal}")

                                    # Convert to microdegrees (optional, if needed)
                                    lat_micro = lat_decimal #* 1_000_000
                                    lon_micro = lon_decimal #* 1_000_000

                                    # Create a Point message for latitude and longitude
                                    gps_coordinates = Point()
                                    gps_coordinates.x = lat_micro  # Latitude
                                    gps_coordinates.y = lon_micro  # Longitude
                                    gps_coordinates.z = 0.0  # You can set this to 0 or leave it as per your requirement

                                    # Publish latitude and longitude in microdegrees
                                    self.publisher_.publish(gps_coordinates)
                                    self.get_logger().info(f"Published: Latitude (microdegrees): {lat_micro}, Longitude (microdegrees): {lon_micro}")
                                else:
                                    self.get_logger().warn("Longitude value is missing in GPGGA sentence.")
                            else:
                                self.get_logger().warn("Latitude value is missing in GPGGA sentence.")
                                gps_coordinates = Point()
                                gps_coordinates.x = 48.766006  # Latitude
                                gps_coordinates.y = 11.434759  # Longitude
                                gps_coordinates.z = 0.0  # You can set this to 0 or leave it as per your requirement

                                    # Publish latitude and longitude in microdegrees
                                self.publisher_.publish(gps_coordinates)
                        except ValueError:
                            self.get_logger().error("Invalid latitude or longitude value in GPGGA sentence.")

def main(args=None):
    rclpy.init(args=args)
    gps_publisher = GPSPublisher()
    
    try:
        gps_publisher.listen_for_gps_data()
    except KeyboardInterrupt:
        pass
    finally:
        gps_publisher.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
