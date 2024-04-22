# betsy_personal_assistant
Introducing Betsy, your personal assistant robot designed to streamline your daily tasks and elevate your workspace experience.

# Conversational AI Robot Control System

This repository contains code for a Conversational AI Robot Control System named Betsy. The system allows users to interact with a robot using voice commands and receive responses from an AI model. The robot can perform various tasks such as following the user, navigating to different locations, and responding to general inquiries.

## Contents

1. [Overview](#overview)
2. [Setup](#setup)
3. [Usage](#usage)
4. [Features](#features)
5. [Contributing](#contributing)
6. [License](#license)

## Overview

The system consists of two main components:

1. **Speech Recognition and AI Interaction**: The `recognize_speech()` function utilizes the SpeechService to recognize voice commands from the user. These commands are then processed by an AI model (OpenAI's GPT-3.5) to generate appropriate responses.

2. **Robot Control and Navigation**: The `handle_user_input()` function interprets the user's commands and triggers actions on the robot accordingly. Actions include moving the robot to different locations, following the user, and providing responses via speech.

## Setup

To set up the system, follow these steps:

1. **Install Dependencies**: Make sure you have Python 3.9 or above installed on your system. Install the required Python packages using the [guide provided in hackster.io](https://www.hackster.io/scuttle-robotics-asia/betsy-personal-office-assistant-8c2a91).

2. **Environment Variables**: Set up environment variables for configuration parameters such as API keys, robot addresses, and component names. Refer to the provided code files for the list of required environment variables.

3. **Robot Configuration**: Ensure that the robot is configured and connected to the network. Update the robot's address and other relevant details in the code as necessary.

## Usage

To use the Conversational AI Robot Control System:

1. Run the main script using the following command:
    ```
    python3 besty.py
    ```

2. Speak into the microphone to issue commands to the robot. The system will recognize your speech, process it using AI, and trigger appropriate actions on the robot.

3. Follow the prompts and instructions provided by the system to interact with the robot effectively.

## Features

- Voice-controlled interaction with the robot.
- AI-powered responses to user commands and inquiries.
- Robot navigation to different locations based on user instructions.
- Integration with external services for speech recognition and AI processing.

## Contributing

Contributions to this project are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the [MIT License](LICENSE).
