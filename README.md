
<div align="center">
	<h1 style="color:#4FC3F7;">💨🌡️ <span style="color:#1976D2;">air-duino</span> 🌱📊</h1>
	<h2 style="color:#43A047;">Monitoramento Inteligente de Qualidade do Ar com ESP32</h2>
	<img src="https://img.shields.io/badge/ESP32-IoT-blue?style=for-the-badge&logo=espressif" alt="ESP32">
	<img src="https://img.shields.io/badge/PostgreSQL-Database-blue?style=for-the-badge&logo=postgresql" alt="PostgreSQL">
	<img src="https://img.shields.io/badge/Projeto-Acadêmico-success?style=for-the-badge" alt="Acadêmico">
</div>

---

## 🎓 Sobre o Projeto

O <b>air-duino</b> é um projeto acadêmico inovador que utiliza a poderosa placa <b>ESP32</b> para monitorar, em tempo real, variáveis ambientais essenciais: <span style="color:#1976D2;">temperatura 🌡️</span>, <span style="color:#388E3C;">umidade 💧</span> e <span style="color:#F44336;">gases tóxicos 🧪</span>. Todos os dados são enviados automaticamente para um banco de dados <b>PostgreSQL</b> para análise, histórico e visualização!

---

## 🚀 Objetivos

- 📡 <b>Monitorar</b> a qualidade do ar em ambientes internos e externos
- ⏰ <b>Agendar</b> coletas periódicas de dados ambientais
- 🗄️ <b>Armazenar</b> informações em um banco de dados robusto (PostgreSQL)
- 📊 <b>Facilitar</b> análises e visualizações para tomada de decisão
- 👨‍🎓 <b>Promover</b> aprendizado prático em IoT, sensores e bancos de dados

---

## 🛠️ Tecnologias Utilizadas

<ul>
	<li>🔌 <b>ESP32</b> — Microcontrolador Wi-Fi/Bluetooth</li>
	<li>🌡️ <b>Sensores de Temperatura</b> (ex: DHT22, LM35)</li>
	<li>💧 <b>Sensores de Umidade</b></li>
	<li>🧪 <b>Sensores de Gás</b> (ex: MQ-2, MQ-135)</li>
	<li>🖥️ <b>Display OLED</b> (opcional, para visualização local)</li>
	<li>🐘 <b>PostgreSQL</b> — Banco de dados relacional</li>
	<li>📡 <b>Wi-Fi</b> — Comunicação de dados</li>
	<li>⏲️ <b>Agendador</b> — Coleta automática em intervalos definidos</li>
</ul>

---

## 🧩 Como Funciona?

<ol>
	<li>O <b>ESP32</b> lê os dados dos sensores de temperatura, umidade e gás.</li>
	<li>Os dados são exibidos no display OLED (se disponível) e enviados via Wi-Fi.</li>
	<li>Um agendador garante que as medições ocorram em intervalos regulares.</li>
	<li>As informações coletadas são armazenadas no <b>PostgreSQL</b> para posterior análise.</li>
</ol>

<div align="center">
	<img src="https://img.icons8.com/color/96/000000/esp32.png" alt="ESP32" width="80"/>
	<img src="https://img.icons8.com/color/96/000000/database.png" alt="Database" width="80"/>
	<img src="https://img.icons8.com/color/96/000000/air-quality.png" alt="Air Quality" width="80"/>
</div>

---

## 📦 Estrutura do Projeto

```text
├── wokwi/
│   ├── main.py           # Código principal do ESP32
│   ├── ssd1306.py        # Driver para display OLED
│   ├── diagram.json      # Esquemático do circuito (Wokwi)
│   └── wokwi-project.txt # Configurações do projeto Wokwi
├── n8n/
│   └── Air Duino.json    # Fluxo de automação (n8n)
├── README.md             # Este arquivo incrível 😎
└── LICENSE               # Licença do projeto
```

---

## 📝 Instalação e Execução

1. <b>Monte o circuito</b> conforme o diagrama em <code>wokwi/diagram.json</code>.
2. <b>Programe o ESP32</b> com o código em <code>wokwi/main.py</code>.
3. <b>Configure o Wi-Fi</b> e os parâmetros do banco de dados PostgreSQL no código.
4. <b>Execute o fluxo de automação</b> (opcional) usando o arquivo <code>n8n/Air Duino.json</code>.
5. <b>Visualize os dados</b> no banco de dados e, se desejar, crie dashboards!

---

## 📚 Aprendizados e Aplicações

- 💡 <b>Internet das Coisas (IoT)</b>: integração de hardware e software
- 🧑‍🔬 <b>Monitoramento ambiental</b>: aplicações em escolas, laboratórios, indústrias e residências
- 🗃️ <b>Banco de dados</b>: modelagem, inserção e consulta de dados reais
- 🕹️ <b>Automação</b>: uso de agendadores e fluxos automáticos

---

## 👨‍💻 Equipe & Créditos

Projeto desenvolvido por [Caio Lima](https://github.com/hyskoniho) e [Jonathan Relva](https://github.com/JhowSantiago)!

---

## 🖼️ Screenshots & Exemplos

<div align="center">
	<img src="https://img.icons8.com/color/96/000000/temperature.png" alt="Temperatura" width="60"/>
	<img src="https://img.icons8.com/color/96/000000/hygrometer.png" alt="Umidade" width="60"/>
	<img src="https://img.icons8.com/color/96/000000/gas.png" alt="Gás" width="60"/>
</div>

---

## 📢 Contato

Fique à vontade para contribuir, sugerir melhorias ou tirar dúvidas!

---

<div align="center">
	<h3 style="color:#43A047;">Feito com ❤️ para a disciplina de IoT!</h3>
</div>
