#Two room heating or cooling
#Caleb Test Program Nov 12
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

#Clearing Room 1 Stepper and DC Motors
kit1 = MotorKit(i2c=board.I2C(), address=0x61)
kit1.motor3.throttle = 0.0
kit1.motor4.throttle = 0.0
kit1.stepper1.release()

#Clearing Room 2 Stepper and DC Motors
kit2 = MotorKit(i2c=board.I2C(), address=0x60)
kit2.motor3.throttle = 0.0
kit2.motor4.throttle = 0.0
kit2.stepper1.release()



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
            if not u_inp.isdigit():
                print("Invalid input. Please enter a number.")
                return
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

# Replace this in the `rooms` function where `root.after` is used
        update_room_info(room_name)

            
        sure = tk.Button(room_frame, text = "Sure", font=('Sans serif', 12), bg = "white", command = store_temp)
        sure.pack(padx=10, pady= 10)
        
        # Schedule the next update after 2 seconds (2000 milliseconds)

        button3 = tk.Button(room_frame, text = "Back", font=('Sans serif', 12), command = lambda:go_back(room_frame))
        button3.pack(padx=0, pady=10)

    root.mainloop()

#Room 1 Asynced Motor Control Function
async def cooling1():
    global preferred_temp
    temp1 = preferred_temp
    if temp1 is not None:
        coolingIn1 = (temperature_f1 - temp1)
        while (True):
            if (coolingIn1 > 0):
                print("Cooling")
                kit1.motor3.throttle = 0.0
                await asyncio.sleep(10.0)
                kit1.motor4.throttle = 1.0
                if abs(temperature_f1 - temp1) <= 1:
                    break
        kit1.motor3.throttle = 0.0
        kit1.motor4.throttle = 0.0

#Room 2 Asynced Motor Control Function
async def Heating2():
    global preferred_temp
    
    temp2 = preferred_temp
    if temp2 is not None:
        heating = (temp2 - temperature_f2)
        while (True):
            if(heating < 0):   
                print("Heating")
                kit2.motor4.throttle = 0.0
                await asyncio.sleep(10.0)
                kit2.motor3.throttle = 1.0
                if abs(temperature_f2 - temp2) <= 1:
                    break
        kit2.motor3.throttle = 0.0
        kit2.motor4.throttle = 0.0

async def update_sensors():
    global temperature_f1, humidity1, temperature_f2, humidity2
    while True:
        try:
            temperature_f1 = sensor1.temperature * (9 / 5) + 32
            humidity1 = sensor1.humidity
            temperature_f2 = sensor2.temperature * (9 / 5) + 32
            humidity2 = sensor2.humidity
            print(f"Room 1 - Temp: {temperature_f1}°F, Humidity: {humidity1}%")
            print(f"Room 2 - Temp: {temperature_f2}°F, Humidity: {humidity2}%")
        except RuntimeError as error:
            print(f"Sensor error: {error.args[0]}")
        await asyncio.sleep(3)  # Delay between sensor readings

async def main():
    # Create tasks for concurrent execution
    task1 = asyncio.create_task(update_sensors())
    task2 = asyncio.create_task(run_gui())
    task3 = asyncio.create_task(cooling1())
    task4 = asyncio.create_task(heating2())
    # Wait for all tasks to complete
    await asyncio.gather(task1, task2, task3, task4)

# Program Entry Point
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")
    finally:
        print("Performing cleanup...")
        del sensor1
        del sensor2
        GPIO.cleanup()
        print("Cleanup complete.")
