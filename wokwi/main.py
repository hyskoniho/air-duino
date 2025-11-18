from machine import ADC, Pin, I2C
from time import sleep
import dht
import network
import time
import ujson
import urequests
import math
import ssd1306   # <-- ADDED

# === Configurações ===
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""
API_URL = "https://primary-production-fb02.up.railway.app/webhook/update-sensor" 

# === Parâmetros MQ-135 ===
RL_VALUE = 10.0 
RO_CLEAN_AIR_FACTOR = 3.6
GAS_CO2 = {"a": 110.47, "b": -2.862} 
GAS_CO  = {"a": 605.18, "b": -3.937}
GAS_NH3 = {"a": 102.2,  "b": -2.473}

# === Hardware ===
adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)
adc.width(ADC.WIDTH_12BIT)

dht_sensor = dht.DHT22(Pin(4))

# --- ADDED: OLED 128×64 ---
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Variável global
Ro = 10.0 

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("--- Conectando ao WiFi... ---")
        wlan.connect(ssid, password)
        timeout = 15
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
            print(".", end="")
        print("")
    
    if wlan.isconnected():
        print(f"WiFi Conectado! IP: {wlan.ifconfig()[0]}")
        return True
    else:
        print("Falha na conexão WiFi.")
        return False

def ler_resistencia_sensor(adc_val):
    voltage = adc_val * (3.3 / 4095.0)
    if voltage == 0: return 0
    if voltage >= 3.3: return 0.1
    rs = ((3.3 * RL_VALUE) / voltage) - RL_VALUE
    return rs

def calibrar_sensor():
    print("\n" + "="*30)
    print("CALIBRANDO SENSOR (AR LIMPO)")
    print("Por favor, aguarde 5 segundos...")
    print("NÃO expor a gases agora.")
    print("="*30)
    
    val_total = 0.0
    for i in range(50):
        val_total += ler_resistencia_sensor(adc.read())
        sleep(0.1)
    
    rs_air = val_total / 50.0
    global Ro
    Ro = rs_air / RO_CLEAN_AIR_FACTOR
    print(f"-> Calibração Concluída. Ro Base: {Ro:.2f} kOhms\n")

def calcular_ppm(rs, gas_curve):
    ratio = rs / Ro
    if ratio <= 0: return 0
    ppm = gas_curve["a"] * math.pow(ratio, gas_curve["b"])
    return ppm

def calcular_aqi(co2, nh3, co):
    score = 0
    status = "Bom (Seguro)"
    
    if co2 > 1000: score += 50
    if nh3 > 10: score += 50
    if co > 10: score += 50
    
    if score > 100: status = "PERIGO (Ruim)"
    elif score > 50: status = "Alerta (Moderado)"
    
    return status

def atualizar_display(temp, hum, ppm_co2, ppm_co, ppm_nh3, aqi_status):
    oled.fill(0)
    oled.text(f"T:{temp:.1f}C H:{hum:.1f}%", 0, 0)
    oled.text(f"CO2:{ppm_co2:.0f}ppm", 0, 15)
    oled.text(f"CO:{ppm_co:.1f} NH3:{ppm_nh3:.1f}", 0, 30)
    oled.text(f"AQI:{aqi_status}", 0, 45)
    oled.show()

def main():
    while not connect_wifi(WIFI_SSID, WIFI_PASS):
        print("Falha. Tentando novamente em 3 segundos...")
        sleep(3)

    calibrar_sensor()

    print("Iniciando Loop de Monitoramento...")

    while True:
        try:
            dht_sensor.measure()
            temp = dht_sensor.temperature()
            hum = dht_sensor.humidity()
            
            adc_raw = adc.read()
            rs_atual = ler_resistencia_sensor(adc_raw)
            
            ppm_co2 = calcular_ppm(rs_atual, GAS_CO2) + 400
            ppm_co  = calcular_ppm(rs_atual, GAS_CO)
            ppm_nh3 = calcular_ppm(rs_atual, GAS_NH3)
            
            aqi_status = calcular_aqi(ppm_co2, ppm_nh3, ppm_co)

            print("-" * 40)
            print(f"AMBIENTE:  Temp: {temp:.1f}°C | Umid: {hum:.1f}%")
            print(f"GASES:     CO2: {ppm_co2:.0f} ppm | CO: {ppm_co:.2f} ppm | NH3: {ppm_nh3:.2f} ppm")
            print(f"SENSOR:    ADC: {adc_raw} | Rs: {rs_atual:.2f} kOhms")
            print(f"STATUS AQI: [{aqi_status}]")

            # === Atualiza o OLED ===
            atualizar_display(temp, hum, ppm_co2, ppm_co, ppm_nh3, aqi_status)

            # === Envio HTTP ===
            dados = {
                "temperatura": temp,
                "umidade": hum,
                "qualidade_ar": {
                    "ppm_co2": round(ppm_co2, 2),
                    "ppm_co": round(ppm_co, 2),
                    "ppm_nh3": round(ppm_nh3, 2),
                },
                "aqi_status": aqi_status
            }
            
            print(">> Enviando dados para nuvem (Railway)...", end=" ")
            response = urequests.post(API_URL, headers={'Content-Type': 'application/json'}, data=ujson.dumps(dados))
            print(f"Status: {response.status_code}")
            response.close()
            print("-" * 40 + "\n")

        except OSError as e:
            print(f"[ERRO] Falha no sensor DHT ou Rede: {e}")
        except Exception as e:
            print(f"[ERRO] Geral: {e}")

        sleep(5)

if __name__ == "__main__":
    main()
