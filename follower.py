import asyncio
import os

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.sensor import Sensor
from viam.components.base import Base
from viam.services.vision import VisionClient
from viam.services.sensors import SensorsClient

robot_api_key = os.getenv('ROBOT_API_KEY') or ''
robot_api_key_id = os.getenv('ROBOT_API_KEY_ID') or ''
robot_address = os.getenv('ROBOT_ADDRESS') or ''
base_name = os.getenv("ROBOT_BASE") or "scuttle_base"
detector_name = os.getenv("ROBOT_DETECTOR") or "myPeopleDetector"
sensor_service_name = os.getenv("ROBOT_SENSORS") or "sensors"
camera_name = os.getenv("ROBOT_CAMERA") or "cam"
pause_interval = os.getenv("PAUSE_INTERVAL") or 3

if isinstance(pause_interval, str):
    pause_interval = int(pause_interval)

base_state = "stopped"

async def connect():
    opts = RobotClient.Options.with_api_key( 
        api_key= robot_api_key,
        api_key_id=robot_api_key_id
    )
    return await RobotClient.at_address(robot_address, opts)

async def person_detect(detector: VisionClient, base: Base, sensors: list[Sensor], sensors_svc: SensorsClient):
    tolerance = 50
    while True:
        print("will detect")
        # Look for person
        detections = await detector.get_detections_from_camera(camera_name)
        frame_width = 640
        frame_height = 480

        obstacle_readings = await get_obstacle_readings(sensors, sensors_svc)
        print("Obstacle Readings:", obstacle_readings)

        person_found = False  # Initialize here
        
        for detection in detections:
            if detection.confidence > 0.4 and detection.class_name == "Person":
                person_found = True
                # Calculate object's center coordinates
                object_center_x = (detection.x_min + detection.x_max) / 2
                object_center_y = (detection.y_min + detection.y_max) / 2
                
                # Calculate distance from object's center to the middle of the frame
                distance_to_middle_x = object_center_x - (frame_width / 2)
                distance_to_middle_y = object_center_y - (frame_height / 2)

                angle = distance_to_middle_x

                if all(reading > 0.4 for reading in obstacle_readings):
                    if abs(distance_to_middle_x) > tolerance :
                        if distance_to_middle_x < 0 :      
                            print("Move left")
                            await base.spin(6, 10)      # CCW is positive
                            # Code to move the robot left
                        else:
                            print("Move right")
                            base_state = "spinning"
                            await base.spin(-4, 10)     # CCW is positive
                            # Code to move the robot right
                    else:
                        print("Object is in the middle")
                        await base.move_straight(distance=150, velocity=50)
        
        # If no person is found and obstacle readings are clear, spin to search for a person
        if not person_found and all(reading > 0.4 for reading in obstacle_readings):
            print("No person detected. Spinning to search.")
            await base.spin(10, 10)
            await asyncio.sleep(2)  # Adjust the delay time as needed
            await base.stop()

async def stop_robot(robot):
    base = Base.from_robot(robot, "scuttle_base")
    await base.stop()

async def get_obstacle_readings(sensors: list[Sensor], sensors_svc: SensorsClient):
    readings = await sensors_svc.get_readings(sensors)
    return [r["distance"] for r in readings.values()]

async def main():
    robot = await connect()
    detector = VisionClient.from_robot(robot, name=detector_name)
    base = Base.from_robot(robot, base_name)
    sensors_svc = SensorsClient.from_robot(robot, sensor_service_name)
    sensors = await sensors_svc.get_sensors()
    person_task = asyncio.create_task(person_detect(detector, base, sensors, sensors_svc))

    await asyncio.gather(person_task)

    await robot.close()

if __name__ == "__main__":
    asyncio.run(main())
