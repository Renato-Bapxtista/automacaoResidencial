# 🚀 Automação Residencial com ESP32 e Node-RED

## 📜 Descrição

Projeto interdisciplinar das disciplinas **Programação para Sistemas Embarcados I** e **Domótica** da **FATEC Jundiaí**.

Este sistema de automação residencial utiliza **ESP32**, sensores e comunicação via **MQTT**, integrado ao **Node-RED**, além de exibir informações em um display **OLED** e enviar alertas via **WhatsApp** usando a API **CallMeBot**.

---

## 🎯 Funcionalidades

- ✅ Leitura de sensores:
  - 🌡️ Temperatura e Umidade (DHT11)
  - 🔥 Gás (MQ2 analógico e digital)
- ✅ Controle de 3 lâmpadas (cozinha, sala e quarto) via:
  - 🖲️ Botões físicos
  - 🖥️ Dashboard Node-RED (via MQTT)
- ✅ Exibição de dados no display **OLED I2C**
- ✅ Envio de alertas WhatsApp:
  - Por botão físico
  - Por detecção de gás em nível crítico
- ✅ Dashboard Web local no ESP32 (opcional)

---

## 🏗️ Arquitetura do Sistema

```plaintext
[Sensor DHT11] ─┐
[Sensor MQ2] ───┤
[Botão Alerta] ─┤── ESP32 ── MQTT ── Node-RED ── Dashboard e WhatsApp
[Botões Lâmpadas] ─┤
[Display OLED] ───┘
```
