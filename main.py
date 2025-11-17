from machine import ADC, Pin, I2C
from time import sleep
import dht
import ssd1306
import network
import time
import usocket as socket
import ussl
import ujson
from umqtt.robust import MQTTClient

# === YOUR WIFI Credentials from WOKWI ===
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""

# === shiftr.io MQTT broker config ===
MQTT_SERVER = "lieking798.cloud.shiftr.io"
MQTT_USER = "lieking798"
MQTT_PASS = "gFE0Psp9HfcqYmOD"
MQTT_TOPIC = "esp32/sensors"

# Initialize Gas (ADC)
adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)
adc.width(ADC.WIDTH_12BIT)

# Initialize DHT22
dht_sensor = dht.DHT22(Pin(4))

# OLED Setup
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Connect to WiFi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(ssid, password)
        timeout = 15  # increase timeout for slower connections
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
    if wlan.isconnected():
        print("Connected, IP:", wlan.ifconfig()[0])
        return True
    else:
        print("Failed to connect to WiFi")
        return False

# Connect and create MQTT client
def mqtt_connect():
    client = MQTTClient(
        client_id="esp32",
        server=MQTT_SERVER,
        user=MQTT_USER,
        password=MQTT_PASS)
    client.connect()
    print("Connected to MQTT broker")
    return client

def main():
    if not connect_wifi(WIFI_SSID, WIFI_PASS):
        oled.fill(0)
        oled.text("WiFi Failed!", 0, 0)
        oled.show()
        return

    try:
        client = mqtt_connect()
    except Exception as e:
        print("MQTT connect error:", e)
        oled.fill(0)
        oled.text("MQTT Connect Fail", 0, 0)
        oled.show()
        return

    while True:
        gas_val = adc.read()

        try:
            dht_sensor.measure()
            temp = dht_sensor.temperature()
            hum = dht_sensor.humidity()

            print("Temp: {:.1f}°C, Humidity: {:.1f}%, Gas: {}".format(temp, hum, gas_val))

            # Prepare JSON data
            data = {
                "temperature": temp,
                "humidity": hum,
                "gas": gas_val
            }
            json_data = ujson.dumps(data)
            client.publish(MQTT_TOPIC, json_data)

            oled.fill(0)
            oled.text("Temp: {:.1f} C".format(temp), 0, 0)
            oled.text("Humidity: {:.1f}%".format(hum), 0, 15)
            oled.text("Gas: {}".format(gas_val), 0, 30)
            oled.show()

        except OSError as e:
            print("Falha DHT22:", e)
            oled.fill(0)
            oled.text("Falha DHT22", 0, 0)
            oled.show()

        except Exception as e:
            print("MQTT publish failed:", e)
            oled.fill(0)
            oled.text("MQTT Pub Fail", 0, 0)
            oled.show()

        sleep(2)


if __name__ == "__main__":
    main()