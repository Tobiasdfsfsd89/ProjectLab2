import asyncio
import adafruit_dht
from adafruit_motorkit import MotorKit
import board
import RPi.GPIO as GPIO
import time
import tkinter as tk

preferred_temp = None
sensor1 = adafruit_dht.DHT22(board.D20)
sensor2 = adafruit_dht.DHT22(board.D21)

# Clearing Room 1 Stepper and DC Motors
kit1 = MotorKit(i2c=board.I2C(), address=0x61)
kit1.motor3.throttle = 0.0
kit1.motor4.throttle = 0.0
kit1.stepper1.release()

# Clearing Room 2 Stepper and DC Motors
kit2 = MotorKit(i2c=board.I2C(), address=0x60)
kit2.motor3.throttle = 0.0
kit2.motor4.throttle = 0.0
kit2.stepper1.release()

async def get_sensor_data():
    """Asynchronously get sensor data and update global variables."""
    global temperature_f1, humidity1, temperature_f2, humidity2
    while True:
        try:
            temperature_f1 = sensor1.temperature * (9 / 5) + 32
            humidity1 = sensor1.humidity

            temperature_f2 = sensor2.temperature * (9 / 5) + 32
            humidity2 = sensor2.humidity

        except RuntimeError as error:
            print(f"Sensor error: {error}")
        await asyncio.sleep(3)  # Non-blocking delay

async def run_gui():
    global preferred_temp
    root = tk.Tk()
    root.geometry("500x500")
    root.title("Group 4 HVAC System")

    label = tk.Label(root, text="HVAC SYSTEM", font=('Sans serif', 20))
    label.pack(padx=150, pady=0)

    def room_1():
        hide_rooms(1)
    def room_2():
        hide_rooms(2)

    main_frame = tk.Frame(root)
    main_frame.pack()

    buttona = tk.Button(main_frame, text="Room 1", command = room_1)
    buttonb = tk.Button(main_frame, text="Room 2", command = room_2)

    buttona.pack(padx=0, pady=10)
    buttonb.pack(padx=0, pady=10)

    def hide_rooms(room_number):
        main_frame.pack_forget() 

        if room_number == 1:
            rooms("Room 1") 
        elif room_number == 2:
            rooms("Room 2")  


    def go_back(room_frame):
        room_frame.pack_forget()
        main_frame.pack()

    def rooms(room_name):

        room_frame = tk.Frame(root)
        room_frame.pack()
        
        room_label = tk.Label(room_frame, text=f"Information for {room_name}", font=('Sans serif', 16))
        room_label.pack(pady=10)
        
        def change_button():
            button1.config(bg = 'light green')
            
        def back_to():
            if button1.cget('bg') == 'light green':
                if button2.cget('activebackground') == 'Orange':
                    button1.config(bg = 'white')
        def store_temp():
            global preferred_temp
            u_inp = pref_temp_text.get("1.0", tk.END).strip()
            temp = int(u_inp)
            while(temp):     
                if temp < 0 or temp > 125:
                    print('Just why are you trying to do this')
                    break
                else:
                    preferred_temp = float(temp)
                    print("User input", temp)
                    
                return preferred_temp
            
        def plusfive():
            temp = store_temp()
            value = temp + 5
            pref_temp_text.delete("1.0", tk.END)
            pref_temp_text.insert(tk.END, str(value))
                
        def minusfive():
            temp = store_temp()
            value = temp - 5
            pref_temp_text.delete("1.0", tk.END)
            pref_temp_text.insert(tk.END, str(value))

        button1 = tk.Button(room_frame, text="Open Register", font=('Sans serif', 12), bg = 'white', command = change_button)
        button1.pack(padx=0, pady=10)

        button2 = tk.Button(room_frame, text="Close Register", font=('Sans serif', 12), bg = 'white', activebackground = 'Orange', command = back_to)
        button2.pack(padx=0, pady=10)

        label_tem = tk.Label(room_frame, text="Temperature", font=('Sans serif', 12))
        label_tem.pack(side='top', pady=10)

        textbox_tem = tk.Text(room_frame, height=1, width=5, font=('Sans serif', 12), borderwidth=5 )
        textbox_tem.pack(side='top', padx=10)

        label_hum = tk.Label(room_frame, text="Humidity", font=('Sans serif', 12))
        label_hum.pack(side='top', pady=10)

        textbox_hum = tk.Text(room_frame, height=1, width=5, font=('Sans serif', 12), borderwidth=5)
        textbox_hum.pack(side='top', padx=10)
        
        Pref_temp_label = tk.Label(room_frame, text="Preferred Temperature", font=('Sans serif', 12))
        Pref_temp_label.pack(side='top', pady=10)
        
        pref_temp_text = tk.Text(room_frame, height=1, width=5, font=('Sans serif', 12), borderwidth=5)
        pref_temp_text.pack(side='top', padx=10)
        
        pref_temp_incre = tk.Button(room_frame, text = "+", font=('Sans serif', 12), bg = "white", command = plusfive)
        pref_temp_incre.pack(side='top', padx=10)
        
        pref_temp_decr = tk.Button(room_frame, text = "- ", font=('Sans serif', 12), bg = "white", command = minusfive)
        pref_temp_decr.pack(side='top', padx=10)
        
        if room_name == "Room 1":   
            textbox_tem.delete("1.0", tk.END)
            textbox_hum.delete("1.0", tk.END)
            
            textbox_tem.insert(tk.END, "{0:0.1f}°F".format(temperature_f1))
            textbox_hum.insert(tk.END, "{0:0.1f}%".format(humidity1))
            
        elif room_name == "Room 2":
            textbox_tem.delete("1.0", tk.END)
            textbox_hum.delete("1.0", tk.END)
            
            textbox_tem.insert(tk.END, "{0:0.1f}°F".format(temperature_f2))
            textbox_hum.insert(tk.END, "{0:0.1f}%".format(humidity2))
            
        sure = tk.Button(room_frame, text = "Sure", font=('Sans serif', 12), bg = "white", command = store_temp)
        sure.pack(padx=10, pady= 10)
        
        # Schedule the next update after 2 seconds (2000 milliseconds)
        root.after(2000, textbox_tem, textbox_hum)

        button3 = tk.Button(room_frame, text = "Back", font=('Sans serif', 12), command = lambda:go_back(room_frame))
        button3.pack(padx=0, pady=10)

    def on_closing():
        # If you need to stop the async loop when GUI closes
        root.quit()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

async def cooling1():
    global preferred_temp
    while True:
        if preferred_temp is not None and temperature_f1 is not None:
            cooling_in1 = (temperature_f1 - preferred_temp)
            if cooling_in1 > 0:
                print("Cooling Room 1")
                kit1.motor3.throttle = 0.0
                kit1.motor4.throttle = 1.0  # Start cooling
                while abs(temperature_f1 - preferred_temp) > 1:
                    await asyncio.sleep(1)  # Non-blocking check
            kit1.motor3.throttle = 0.0
            kit1.motor4.throttle = 0.0
        await asyncio.sleep(10)

async def heating2():
    global preferred_temp
    while True:
        if preferred_temp is not None and temperature_f2 is not None:
            heating_in2 = (preferred_temp - temperature_f2)
            if heating_in2 > 0:
                print("Heating Room 2")
                kit2.motor4.throttle = 0.0
                kit2.motor3.throttle = 1.0  # Start heating
                while abs(temperature_f2 - preferred_temp) > 1:
                    await asyncio.sleep(1)  # Non-blocking check
            kit2.motor3.throttle = 0.0
            kit2.motor4.throttle = 0.0
        await asyncio.sleep(10)

async def main():
    # Create asynchronous tasks
    gui_task = asyncio.create_task(run_gui())
    sensor_task = asyncio.create_task(get_sensor_data())
    cooling_task = asyncio.create_task(cooling1())
    heating_task = asyncio.create_task(heating2())

    await asyncio.gather(gui_task, sensor_task, cooling_task, heating_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        sensor1.exit()
        sensor2.exit()
        GPIO.cleanup()
