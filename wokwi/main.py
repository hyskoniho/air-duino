from machine import ADC, Pin, I2C
from time import sleep
import dht
import network
import time
import ujson
import urequests
import math
import ssd1306

# === Configurações ===
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""
API_URL = "https://primary-production-638b.up.railway.app/webhook/update-sensor" 

# === Parâmetros das Curvas MQ-135 (a, b) ===
# Fonte baseada em datasheets padrão do MQ-135
RL_VALUE = 10.0 
RO_CLEAN_AIR_FACTOR = 3.6

# Gases já existentes
GAS_CO2 = {"a": 110.47, "b": -2.862} 
GAS_CO  = {"a": 605.18, "b": -3.937}
GAS_NH3 = {"a": 102.2,  "b": -2.473} # Amônia

# --- NOVOS GASES ADICIONADOS ---
GAS_ALCOHOL = {"a": 77.255, "b": -3.18}  # Álcool/Etanol
GAS_BENZENE = {"a": 44.947, "b": -3.445} # Benzeno (Tolueno similar)
GAS_ACETONE = {"a": 34.434, "b": -3.369} # Acetona

# === Hardware ===
adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)
adc.width(ADC.WIDTH_12BIT)

dht_sensor = dht.DHT22(Pin(4))

# OLED 128x64
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Variável global
Ro = 10.0 
display_page = 0  # Para alternar telas no OLED

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
    if voltage >= 3.3: return 0.1 # Evitar divisão por zero se saturar
    rs = ((3.3 * RL_VALUE) / voltage) - RL_VALUE
    return rs

def calibrar_sensor():
    print("\n" + "="*30)
    print("CALIBRANDO SENSOR (AR LIMPO)")
    oled.fill(0)
    oled.text("CALIBRANDO...", 10, 30)
    oled.show()
    
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
    # Fórmula: PPM = a * (Rs/Ro)^b
    ppm = gas_curve["a"] * math.pow(ratio, gas_curve["b"])
    return ppm

def calcular_aqi(co2, nh3, co, alc):
    score = 0
    status = "Bom"
    
    # Critérios simplificados para exemplo
    if co2 > 1000: score += 30
    if nh3 > 10: score += 40
    if co > 10: score += 40
    if alc > 100: score += 20
    
    if score > 80: status = "PERIGO"
    elif score > 40: status = "Alerta"
    
    return status

def atualizar_display_paginado(temp, hum, co2, co, nh3, alc, ben, aqi):
    global display_page
    oled.fill(0)
    
    if display_page == 0:
        # TELA 1: Clima e Gases Comuns
        oled.text(f"T:{temp:.1f}C H:{hum:.0f}%", 0, 0)
        oled.text("-" * 16, 0, 10)
        oled.text(f"CO2: {co2:.0f} ppm", 0, 20)
        oled.text(f"CO : {co:.2f} ppm", 0, 30)
        oled.text(f"Sts: {aqi}", 0, 50)
        oled.text(">> Pag 1/2", 80, 55)
    else:
        # TELA 2: Químicos / Tóxicos
        oled.text("QUIMICOS (ppm)", 0, 0)
        oled.text("-" * 16, 0, 10)
        oled.text(f"NH3: {nh3:.2f}", 0, 20)
        oled.text(f"Alc: {alc:.2f}", 0, 30)
        oled.text(f"Ben: {ben:.2f}", 0, 40)
        oled.text(">> Pag 2/2", 80, 55)

    oled.show()
    # Alterna página para o próximo ciclo
    display_page = 1 if display_page == 0 else 0

def main():
    while not connect_wifi(WIFI_SSID, WIFI_PASS):
        print("Falha. Tentando novamente em 3 segundos...")
        sleep(3)

    calibrar_sensor()

    print("Iniciando Loop de Monitoramento Completo...")

    while True:
        try:
            dht_sensor.measure()
            temp = dht_sensor.temperature()
            hum = dht_sensor.humidity()
            
            adc_raw = adc.read()
            rs_atual = ler_resistencia_sensor(adc_raw)
            
            # === CÁLCULO DE TODOS OS GASES ===
            # Nota: CO2 adicionamos +400 de base atmosférica estimada
            ppm_co2 = calcular_ppm(rs_atual, GAS_CO2) + 400 
            ppm_co  = calcular_ppm(rs_atual, GAS_CO)
            ppm_nh3 = calcular_ppm(rs_atual, GAS_NH3)
            ppm_alc = calcular_ppm(rs_atual, GAS_ALCOHOL)
            ppm_ben = calcular_ppm(rs_atual, GAS_BENZENE)
            ppm_ace = calcular_ppm(rs_atual, GAS_ACETONE)
            
            aqi_status = calcular_aqi(ppm_co2, ppm_nh3, ppm_co, ppm_alc)

            # Log Serial
            print("-" * 40)
            print(f"AMB: T:{temp:.1f}C H:{hum:.1f}% | Rs:{rs_atual:.2f}k")
            print(f"Ar : CO2:{ppm_co2:.0f} | CO:{ppm_co:.2f}")
            print(f"Quim: NH3:{ppm_nh3:.2f} | Alc:{ppm_alc:.2f} | Ben:{ppm_ben:.2f} | Ace:{ppm_ace:.2f}")
            print(f"STATUS: [{aqi_status}]")

            # === Atualiza o OLED (Paginado) ===
            atualizar_display_paginado(temp, hum, ppm_co2, ppm_co, ppm_nh3, ppm_alc, ppm_ben, aqi_status)

            # === Envio HTTP Completo ===
            dados = {
                "temperatura": temp,
                "umidade": hum,
                "gases": {
                    "co2": round(ppm_co2, 2),
                    "co": round(ppm_co, 2),
                    "nh3": round(ppm_nh3, 2),
                    "alcool": round(ppm_alc, 2),
                    "benzeno": round(ppm_ben, 2),
                    "acetona": round(ppm_ace, 2)
                },
                "sensor_raw": {
                    "adc": adc_raw,
                    "rs_ohm": round(rs_atual, 2)
                },
                "aqi_status": aqi_status
            }
            
            print(">> Enviando webhook...", end=" ")
            # Timeout curto para não travar o display
            response = urequests.post(API_URL, headers={'Content-Type': 'application/json'}, data=ujson.dumps(dados))
            print(f"Status: {response.status_code}")
            response.close()
            print("-" * 40 + "\n")

        except OSError as e:
            print(f"[ERRO DE REDE/SENSOR]: {e}")
            # Tenta reconectar se perder WiFi
            if not network.WLAN(network.STA_IF).isconnected():
                connect_wifi(WIFI_SSID, WIFI_PASS)
        except Exception as e:
            print(f"[ERRO GERAL]: {e}")

        # Delay entre leituras (e alternância de tela)
        sleep(3)

if __name__ == "__main__":
    main()