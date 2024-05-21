# IoT Device Code Documentation

This documentation outlines the functionality and configuration of an IoT device using a Raspberry Pi Pico (RPi Pico) microcontroller. The device connects to an MQTT broker and reads temperature data from a sensor. Here are the key components and features:

## Components:
- Raspberry Pi Pico (RPi Pico) microcontroller
- Temperature sensor (connected to ADC pin 4)
- LEDs (green and red) for status indication
- Push button (connected to pin 14)

## Configuration:
1. **Network Connection:**
   - The device connects to a Wi-Fi network specified in the `config.SSID` and `config.PASSWORD` variables.
   - Ensure that the Wi-Fi credentials are correctly set in the `config.py` file.

2. **Temperature Sensor:**
   - The `sensor_temp` reads temperature data from the analog pin (ADC pin 4).
   - The `conversion_factor` converts the ADC reading to voltage.
   - The `dif_sensor_temp` accounts for the temperature difference between the RPi Pico and the environment.

3. **Time Synchronization:**
   - The device synchronizes its time with an NTP server (`pool.ntp.org`).
   - The `GMT_OFFSET` adjusts for the local time zone (e.g., 3600 seconds for summer time).

4. **MQTT Communication:**
   - The `mqtt_connect()` function establishes an SSL-secured MQTT connection to an IoT hub.
   - The Digicert certificate (`digicert.cer`) is loaded for secure communication.
   - The `callback_handler()` function processes received MQTT messages (e.g., turning on/off LEDs).

5. **LED Indication:**
   - The green LED (pin 15) indicates successful MQTT connection.
   - The red LED (pin 13) indicates network connection status.

6. **Button Press:**
   - The push button (pin 14) triggers an MQTT message when pressed.

7. **RTC (Real-Time Clock):**
   - The device maintains accurate time using the RTC.
   - The `getTimeNTP()` function retrieves time from the NTP server.
   - The `setTimeRTC()` function sets the RTC time based on NTP data.

## Usage:
1. Upload this code to your RPi Pico.
2. Ensure that the `config.py` file contains correct Wi-Fi and MQTT broker details.
3. Monitor the device status via the LEDs and MQTT communication.
