import paho.mqtt.client as mqtt
import time
import math

target_current = 0
current_power = 0
current_temp = 0
old_set = 0
is_on = 0

def on_message(client, _userdata, message):
    global target_current
    global current_power
    global current_temp
    global is_on
    if message.topic == "heatpump_control/maxCurrent":
        target_current = int(message.payload)
    elif message.topic == "panasonic_heat_pump/s0/Watt/1":
        current_power = int(message.payload)
    elif message.topic == "panasonic_heat_pump/main/Main_Outlet_Temp":
        current_temp = int(message.payload)
    else:
        is_on = int(message.payload)


broker = "car.devpi.de"

client = mqtt.Client("heatpump_control_client")
client.connect(broker)

client.loop_start()

# subscribe to mqtt topic
# evcc target power = evcc controlled power value that heatpump should reach
client.subscribe("heatpump_control/maxCurrent")
client.subscribe("panasonic_heat_pump/s0/Watt/1")
client.subscribe("panasonic_heat_pump/main/Main_Outlet_Temp")
client.subscribe("panasonic_heat_pump/main/Heatpump_State")

client.on_message = on_message

# position gain
kp = 0.1

while True:
    target_power = target_current * 230  # P = U * I
    u = math.trunc(kp * (target_power-current_power))
    new_temp = u + current_temp
    if new_temp > 60:
        new_temp = 60
    if new_temp < 30:
        new_temp = 30
    print("new temperature: ", new_temp)
    if new_temp != old_set and is_on == 1:
        client.publish(
            "panasonic_heat_pump/commands/SetZ1HeatRequestTemperature", new_temp)
        old_set = new_temp
    # client.publish("base_topic/commands/SetZ2HeatRequestTemperature", u + current_temp)
    time.sleep(15)
