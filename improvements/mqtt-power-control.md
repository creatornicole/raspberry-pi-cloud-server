## ⚡ MQTT Power Control


= Message Queuing Telemetry Transport
- lightweight, publish-subscribe messaging protocol
- designed for low-bandwidth, high-latency or unreliable networks
- widely used in IoT applications where devices (e.g. sensors, plugs, thermostats) need to send or receive data efficiently
- broker needed

| Key Concept | Description                                                                                                                 |
| ----------- | --------------------------------------------------------------------------------------------------------------------------- |
| Broker      | central server that manages messages; devices don't talk to each other directly - they go through the broker                |
| Client      | any device or application that connects to the broker; clients can publish messages or subscribe to topics                  |
| Topic       | a string like ```home/livingroom/lamp``` that helps organize messages; clients subscribe to topics to receive relevant data |
| Publish     | client sends a message to a topic                                                                                           |
| Subscribe   | client tells broker it wants messages from a specific topic                                                                 |

- need to enable MQTT on Shelly Plug

> Once you enable MQTT on your Shelly Plug, MQTT takes over the control - so the Shelly app usually can't control the device at the same time


- this means
	- Python script (here) will control the device
	- Shelly app can no longer be used to turn it on/off (only in local network)
	- if you want to control your Shelly Plug via Python and MQTT, you have to accept that the Shelly app won't be able to control the plug (or only very limited)
	- you can still use the Shelly app for status updates, but control commands must go via MQTT
- reasons
	- Shelly disables cloud-based control commands when MQTT control is active to avoid conflicts
	- MQTT control happens "directly" through your broker to the device


#### Setup

| Role       | Device/Software                                                    | Notes                                                                                                   |
| ---------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| Subscriber | Shelly Plug S Gen3                                                 | listens to MQTT commands (e.g. "on"/"off") = subscribes to the topic and siwtches on or off accordingly |
| Publisher  | Python script on PC                                                | sends/ publishes MQTT messages to a topic to control the plug                                           |
| Broker     | [HiveMQ Cloud](https://www.hivemq.com/products/mqtt-cloud-broker/) | routes messages between publisher and subscriber                                                        |

#### HiveMQ Cloud as a Cloud Broker

- pretty easy: go to https://www.hivemq.com/index-alt/ -> Click "Start Free" -> "Sign Up Free Now" for the "HiveMQ Cloud" -> Sign Up -> Create Serverless Cluster (it's free!)