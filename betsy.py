import asyncio
import os
import re
import subprocess
from viam.robot.client import RobotClient
from viam.rpc.dial import DialOptions
from chat_service_api import Chat
from speech_service_api import SpeechService
import openai
import spotipy
from viam.components.base import Base
from viam.services.sensors import SensorsClient
from viam.components.sensor import Sensor

robot_api_key = os.getenv('ROBOT_API_KEY') or ''
robot_api_key_id = os.getenv('ROBOT_API_KEY_ID') or ''
robot_address = os.getenv('ROBOT_ADDRESS') or ''
base_name = os.getenv("ROBOT_BASE") or "scuttle_base"
detector_name = os.getenv("ROBOT_DETECTOR") or "myPeopleDetector"
sensor_service_name = os.getenv("ROBOT_SENSORS") or "sensors"
camera_name = os.getenv("ROBOT_CAMERA") or "cam"
pause_interval = os.getenv("PAUSE_INTERVAL") or 3


openai.api_key = os.getenv("OPENAI_API_KEY") or "Enter open ai API key"

# Global variables
base_state = "stopped"
current_location = "base"
following_mode = False

# Connect to the robot
async def connect():
    opts = RobotClient.Options.with_api_key(api_key=robot_api_key, api_key_id=robot_api_key_id)
    return await RobotClient.at_address(robot_address, opts)

# Recognize speech using the SpeechService
async def recognize_speech():
    robot = await connect()
    speech = SpeechService.from_robot(robot, name='speech')
    
    while True:
        commands = await speech.get_commands(1)
        if commands:
            command = commands[0]
            print("Command:", command)
            await robot.close()
            return command

# Query AI for response
async def query(payload):
    completion = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        max_tokens=256,
        messages=[{"role": "user", "content": payload}]
    )
    msg = completion.choices[0].message
    out = msg['content']
    return out

# Main chat function
async def chat():
    global following_mode
    robot = await connect()
    speech = SpeechService.from_robot(robot, name='speech')
    base = Base.from_robot(robot, name=base_name)
    sensors_svc = SensorsClient.from_robot(robot, sensor_service_name)
    sensors = await sensors_svc.get_sensors()
    
    print("You can speak now. You can stop the conversation by saying 'exit'.")
    while True:
        user_input = await recognize_speech()
        print(user_input)
        prompt = "You are betsy As a personal assistant robot, you have 4 functionalities: 1. Following me, 2.Going from the base to Yogen's desk, 3.Going from Yogen's desk to Fad/Faddulah's desk and exit. When you recive input, you will respond with one of the following options: Function 1, Function 2, Function 3 or Exit. If the input is not related to these functionalities, you will answer appropiately to the question."
        user_input = await query(prompt + user_input)
        print(user_input)
        await handle_user_input(user_input, robot, speech, base, sensors_svc)

# Handle user input based on commands
async def handle_user_input(user_input, robot, speech, base, sensors_svc):
    global current_location
    global following_mode
    
    if user_input.lower() == "exit":
        print("Exiting conversation...")
        return
    
    if user_input.lower() == "function 1":
        print("Following you...")
        following_mode = True
        subprocess.run(["python3", "follower.py"])
        return
    
    if user_input.lower() == "function 2" and current_location != "station a":
        await base_to_yogen_desk(robot, user_input, speech, base, sensors_svc)
        return
    
    if user_input.lower() == "function 3" and current_location != "station a":
        await yogen_desk_to_fad_desk(robot, user_input, speech)
        return
    
    response = user_input
    clean_response = re.sub(r'\n', '', response)
    print("AI:", clean_response)
    await speech.say(clean_response, True)

# Move robot to Yogen's desk
async def base_to_yogen_desk(robot, user_input, speech, base, sensors_svc):
    global current_location
    print("Going to Yogen's desk")
    await base.move_straight(distance=2000, velocity=10)
    await base.stop()
    
    if "tell" in user_input.lower():
        message_to_repeat = re.search(r'(?<=tell\s)(.*)', user_input.lower()).group(1)
        await speech.say("You were told: " + message_to_repeat, True)
    
    current_location = "station a"
    await update_robot_location(current_location)

# Get obstacle readings from sensors
async def get_obstacle_readings(sensors, sensors_svc):
    readings = await sensors_svc.get_readings(sensors)
    return [r["distance"] for r in readings.values()]

# Move robot to Faddulah's desk
async def yogen_desk_to_fad_desk(robot, user_input, speech):
    global current_location
    print("Going to Faddulah's desk")
    await base.spin(angle=45, velocity=20)
    await base.stop()
    await base.move_straight(distance=2000, velocity=100)
    await base.stop()
    
    if "tell" in user_input.lower():
        message_to_repeat = re.search(r'(?<=tell\s)(.*)', user_input.lower()).group(1)
        await speech.say("You were told: " + message_to_repeat, True)
    
    current_location = "station b"
    await update_robot_location(current_location)

# Update robot's current location
async def update_robot_location(location):
    print("Robot location updated:", location)

# Main function to run the chat
async def main():
    await chat()

if __name__ == "__main__":
    asyncio.run(main())
