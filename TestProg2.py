from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
import threading
import time
import asyncio
import adafruit_dht
from adafruit_motorkit import MotorKit
import board
import RPi.GPIO as GPIO
import tkinter as tk


relayPin1 = 5   
relayPin2 = 6


factory = PiGPIOFactory()
servo = Servo(19, pin_factory=factory)

servo.value = -.67

preferred_temp = 0
temperature_f1 = 0
humidity1 = 0
temperature_f2 = 0
humidity2 = 0
picked_room = None
sensor1 = adafruit_dht.DHT22(board.D17)
sensor2 = adafruit_dht.DHT22(board.D27)

#Clearing Room 1 Stepper and DC Motors
kit1 = MotorKit(i2c=board.I2C(), address=0x60)
kit1.motor3.throttle = 0.0
kit1.motor4.throttle = 0.0

#Clearing Room 2 Stepper and DC Motors
kit2 = MotorKit(i2c=board.I2C(), address=0x61)
kit2.motor3.throttle = 0.0
kit2.motor4.throttle = 0.0



def run_gui():
    global preferred_temp
    global picked_room
    root = tk.Tk()

    root.geometry("500x500")
    root.title("Group 4 HVAC System")

    label = tk.Label(root, text="HVAC SYSTEM", font=('Sans serif', 20))
    label.pack(padx=150, pady=0)

    def room_1():
        global picked_room
        picked_room = "Room 1"
        print(f"Picked Room: {picked_room}")
        hide_rooms(1)
    def room_2():
        global picked_room
        picked_room = "Room 2"
        print(f"Picked Room: {picked_room}")
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
            if not u_inp.isdigit():
                print("Invalid input. Please enter a number.")
            temp = float(u_inp)
            while(temp):     
                if temp < 0 or temp > 125:
                    print('Just why are you trying to do this')
                    break
                else:
                    preferred_temp = float(temp)
                    print("User input", temp)
                    return preferred_temp
            
        def plusfive():
            preferred_temp = store_temp()
            value = preferred_temp + 5
            pref_temp_text.delete("1.0", tk.END)
            pref_temp_text.insert(tk.END, str(value))
                
        def minusfive():
            preferred_temp = store_temp()
            value = preferred_temp - 5
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
        
        def update_room_info(room_name):
            if room_name == "Room 1":
                temperature = temperature_f1
                humidity = humidity1
            elif room_name == "Room 2":
                temperature = temperature_f2
                humidity = humidity2
        
            textbox_tem.delete("1.0", tk.END)
            textbox_hum.delete("1.0", tk.END)
            textbox_tem.insert(tk.END, f"{temperature:.1f}°F")
            textbox_hum.insert(tk.END, f"{humidity:.1f}%")
        
            # Schedule the next update
            root.after(2000, lambda: update_room_info(room_name))

        update_room_info(room_name)

            
        sure = tk.Button(room_frame, text = "Sure", font=('Sans serif', 12), bg = "white", command = store_temp)
        sure.pack(padx=10, pady= 10)
        
        # Schedule the next update after 2 seconds (2000 milliseconds)

        button3 = tk.Button(room_frame, text = "Back", font=('Sans serif', 12), command = lambda:go_back(room_frame))
        button3.pack(padx=0, pady=10)

    root.mainloop()

def set_servo_angle(angle):
    # Map angle (0 to 180) to the servo range (-1 to 1)
    if angle < 0:
        angle = 0
    if angle > 180:
        angle = 180
    # Map 0° -> -1, 180° -> 1
    servo_value = (angle / 90) - 1
    servo.value = servo_value

def stop_servo():
    servo.value = None
    
async def cooling1():
    global temperature_f1, preferred_temp

    while True:
        if preferred_temp and temperature_f1 > preferred_temp:
            print("Cooling Room 1")
            coolingIn1 = temperature_f1 - preferred_temp
            set_servo_angle(180) 
            sleep(2)  
            stop_servo()        
            if abs(temperature_f1 - preferred_temp) <= 1:
                print("Cooling completed: Room 1")
                set_servo_angle(30)
                sleep(2)  
                stop_servo()
                kit1.motor4.throttle = 0.0  
                break

        await asyncio.sleep(2)

async def Heating2():
    global preferred_temp
    
    temp2 = preferred_temp
    if temp2 is not None:
        heating = (temp2 - temperature_f2)
        while (True):
            if(heating > 0):   
                print("Heating")
                GPIO.output(relayPin1, GPIO.HIGH)  
                print("Fan 1: ON")
                await asyncio.sleep(10.0)
                kit2.motor3.throttle = 1.0
                if abs(temperature_f2 - temp2) <= 1:
                    GPIO.output(relayPin1, GPIO.LOW)  
                    print("Fan 2:LOW")
                    break
        kit2.motor3.throttle = 0.0
        kit2.motor4.throttle = 0.0

async def update_sensors():
    global temperature_f1, humidity1, temperature_f2, humidity2
    try:
        temperature_f1 = sensor1.temperature * (9 / 5) + 32
        humidity1 = sensor1.humidity
        temperature_f2 = sensor2.temperature * (9 / 5) + 32
        humidity2 = sensor2.humidity
        print(f"Room 1 - Temp: {temperature_f1}°F, Humidity: {humidity1}%")
        print(f"Room 2 - Temp: {temperature_f2}°F, Humidity: {humidity2}%")
    except RuntimeError as error:
        print(f"Sensor error: {error.args[0]}")
    await asyncio.sleep(0.1) # Delay between sensor readings



async def start_gui_thread():
    print("Initizaling GUI Thread")
    background_thread1 = threading.Thread(target = run_gui, daemon = True)
    background_thread1.start()
    await asyncio.sleep(0.1)
    
async def main():
    global picked_room
    await asyncio.create_task(update_sensors()) 
    await start_gui_thread()  # Start GUI in a separate thread
    

    if picked_room == "Room 1":
        print("Starting cooling for Room 1")
        task1 = asyncio.create_task(cooling1())
        await task1

    elif picked_room == "Room 2":
        print("Starting heating for Room 2")
        task1.cancel()
        task2 = asyncio.create_task(Heating2())
        await task2

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")
        print("Performing cleanup...")
        sensor1.exit()
        sensor2.exit()
        GPIO.cleanup()
        print("Cleanup complete.")
