import paho.mqtt.client as mqtt
import time

target_current = 0
current_power = 0
current_temp = 0

def on_message(client, useradata, message):
    global target_current
    global current_power
    if message.topic == "evcc/loadpoints/2/maxCurrent":
        target_current = int(message.payload)
    else:
        current_power = int(message.payload)

broker = "car.devpi.de"

client = mqtt.Client("heatpump_control")
client.connect(broker)

client.loop_start()

# subscribe to mqtt topic
# evcc target power = evcc controlled power value that heatpump should reach
client.subscribe("evcc/loadpoints/2/maxCurrent")
client.subscribe("panasonic_heat_pump/s0/Watt/1")

client.on_message = on_message

# position gain
kp = 0.1

while True:
    target_power = target_current * 220 # P = U * I
    u = kp * (target_current-current_power)
    client.publish("base_topic/commands/SetZ1HeatRequestTemperature", u + current_temp)
    client.publish("base_topic/commands/SetZ2HeatRequestTemperature", u + current_temp)
    time.sleep(20)