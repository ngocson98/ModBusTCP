from pymodbus.client.sync import ModbusTcpClient
from pymodbus.framer.socket_framer import ModbusSocketFramer
import time
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime

# Global variables for settings
host = '127.0.0.1'
port = 502
function_code = 4
starting_address = 0
num_registers = 6
# register_names = []
register_names = [""] * num_registers
scanRate = 1000  # Time interval for reading data

# Initialize main window
window = tk.Tk()
window.title("Modbus TCP/IP")
window.geometry("640x480")

# Modbus client setup
client = None
connected = False


def connect_to_modbus():
    global client, connected
    client = ModbusTcpClient(host, port, framer=ModbusSocketFramer)
    connected = client.connect()
    if connected:
        messagebox.showinfo("Connection Status", "Connected to Modbus server")
        # connected = True
    else:
        messagebox.showerror("Connection Status", "Failed to connect to Modbus server")
        # connected = False


# Read Modbus data function
def read_data():
    global connected, register_names
    connect_to_modbus()
    # register_names = [""] * num_registers
    # print(f"Connected: {connected}")
    # if not connected:
    #     messagebox.showerror("Connection Status", "Not connected to Modbus server")
    #     return
    year = str(datetime.now().year)
    month = str(datetime.now().month).zfill(2)
    day = str(datetime.now().day).zfill(2)

    # client = ModbusTcpClient(host, port, framer=ModbusSocketFramer)
    # connected = client.connect()
    # print(f"Connected: {connected}")
    if connected:
        try:
            while True:
                prev = None
                response = client.read_input_registers(starting_address, num_registers, unit=1)

                if response.isError():
                    print(f"Error reading registers: {response}")
                else:
                    print(f"Registers read: {response.registers}")
                    table.delete(*table.get_children())
                    if response.registers == prev:
                        pass
                    else:
                        prev = response.registers
                        for i, value in enumerate(response.registers):
                            if i < len(register_names) and register_names[i]:
                                table.insert("", "end", values=(register_names[i], value))
                            else:
                                table.insert("", "end", values=(f"Value {i + starting_address}", value))

                with open(f"data{year}{month}{day}.csv", 'a') as f:
                    f.write(",".join(map(str, response.registers)) + ',' + str(datetime.now()) + "\n")

                time.sleep(scanRate / 1000)
        except Exception as e:
            print("ERROR:", e)
        finally:
            client.close()
            print("Connection closed.")
    else:
        print("Failed to connect to Modbus server.")


# Setting window for Modbus parameters
def open_setting_window():
    setting_window = tk.Toplevel(window)
    setting_window.title("Settings")
    setting_window.geometry("300x400")

    tk.Label(setting_window, text="Host:").pack()
    host_entry = tk.Entry(setting_window, width=30)
    host_entry.insert(0, host)
    host_entry.pack()

    tk.Label(setting_window, text="Port:").pack()
    port_entry = tk.Entry(setting_window, width=30)
    port_entry.insert(0, port)
    port_entry.pack()

    tk.Label(setting_window, text="Function Code:").pack()
    lstFunc = ['01 Read Coils (0x)', '02 Read Discrete Inputs (1x)', '03 Read Holding Registers (4x)',
               '04 Read Input Registers (3x)', '05 Write Single Coil', '06 Write Single Register',
               '15 Write Multiple Coils', '16 Write Miltiple Registers']
    function_code_combo = ttk.Combobox(setting_window, values=lstFunc, width=27)
    function_code_combo.set(lstFunc[3])  # Default selection
    function_code_combo.pack()

    tk.Label(setting_window, text="Starting Address:").pack()
    starting_address_combo = ttk.Combobox(setting_window, values=list(range(11)), width=27)
    starting_address_combo.set(starting_address)  # Default selection
    starting_address_combo.pack()

    tk.Label(setting_window, text="Number of Registers:").pack()
    num_register_spinbox = tk.Spinbox(setting_window, from_=1, to=10, width=28)
    num_register_spinbox.delete(0, "end")
    num_register_spinbox.insert(0, num_registers)
    num_register_spinbox.pack()

    tk.Label(setting_window, text="Scan Time (ms):").pack()
    time_entry = tk.Entry(setting_window, width=30)
    time_entry.insert(0, scanRate)
    time_entry.pack()

    def apply_settings():
        global host, port, starting_address, num_registers, scanRate, function_code
        host = host_entry.get()
        port = int(port_entry.get())
        function_code = int(function_code_combo.get().split()[0])
        starting_address = int(starting_address_combo.get())
        num_registers = int(num_register_spinbox.get())
        scanRate = int(time_entry.get())
        setting_window.destroy()
        update_table()
        # update_info_label()
        # update_Status()
        connect_to_modbus()

    def cancel_settings():
        setting_window.destroy()

    xOK = 200
    yOK = 260
    tk.Button(setting_window, text="OK", command=apply_settings, width=5).place(x=xOK, y=yOK)
    # tk.Button(setting_window, text="Cancel", command=cancel_settings).place(x=xOK-15, y=yOK+50)


def register_names_window():
    global register_names, num_registers
    if len(register_names) < num_registers:
        register_names.extend([""] * (num_registers - len(register_names)))
    # Create a new window for entering register names
    register_window = tk.Toplevel(window)
    register_window.title("Register Names")
    register_window.geometry("300x400")

    # Create a frame to hold the entries
    frame = tk.Frame(register_window)
    frame.pack(pady=10)

    # Create labels and entry fields for each register
    entries = []
    for i in range(starting_address, starting_address + num_registers):
        label = tk.Label(frame, text=f"Register {i}:")
        label.grid(row=i-starting_address, column=0, padx=10, pady=5)

        entry = tk.Entry(frame, width=30)
        # entry.insert(0, register_names[i])  # Set default value if exists
        entry.insert(0, register_names[i-starting_address] if (i-starting_address) < len(register_names) else "")
        entry.grid(row=i-starting_address, column=1, padx=10, pady=5)

        entries.append(entry)  # Add entry to list for later access

    def save_register_names():
        for i, entry in enumerate(entries):
            register_names[i] = entry.get()  # Save entered name to global list
        print(register_names)
        messagebox.showinfo("Success", "Register names saved successfully!")
        register_window.destroy()  # Close the window

    # Add an OK button to save names and close the window
    ok_button = tk.Button(register_window, text="OK", command=save_register_names)
    ok_button.pack(pady=10)


# Update table according to num_registers
def update_table():
    # Clear current rows
    for col in table["columns"]:
        table.heading(col, text="")
        table.delete(*table.get_children())

    # columns = [f"Reg {i}" for i in range(num_registers)]
    columns = ["Register", "Value"]
    table["columns"] = columns

    # update title and size col
    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=80, anchor="center")


def update_info_label():
    info_text = f"Host: {host} | Port: {port} | Function Code: {function_code} | " \
                f"Num Registers: {num_registers} | Scan Rate: {scanRate} ms"
    info_label.config(text=info_text)


def update_Status():
    if connected:
        status_text = f"Status: {connected}"
        status_label.config(text=status_text, fg="green")
    else:
        status_text = f"Status: {connected}"
        status_label.config(text=status_text, fg="red")


def update_interface():
    update_info_label()
    update_Status()
    window.after(1000, update_interface)


# Set up main UI elements
menu_bar = tk.Menu(window)
setting_menu = tk.Menu(menu_bar, tearoff=0)
setting_menu.add_command(label="Settings", command=open_setting_window)
setting_menu.add_command(label="Register Names", command=register_names_window)
menu_bar.add_cascade(label="Menu", menu=setting_menu)
window.config(menu=menu_bar)

# Display configuration information and connection status
info_frame = tk.Frame(window)
info_frame.pack(pady=10)
info_label = tk.Label(info_frame, text="", font=("Arial", 10), fg="black")
info_label.pack()
status_label = tk.Label(info_frame, text="", font=("Arial", 10))
status_label.pack()

# Create table to display register data
table_frame = tk.Frame(window)
table_frame.pack(pady=15)
table = ttk.Treeview(table_frame, columns=["Register", "Value"], show="headings")
# table = ttk.Treeview(table_frame, columns=[f"Reg {i}" for i in range(num_registers)], show="headings")
table.pack()

connect_to_modbus()
update_table()  # Initialize table structure based on default num_registers
update_info_label()
update_Status()


# Start Modbus data reading in a new thread
# thread = threading.Thread(target=read_data)
# thread.daemon = True  # Ensure the thread will exit when the program closes
# thread.start()
def connect_to_modbus():
    global client, connected, read_thread
    client = ModbusTcpClient(host, port, framer=ModbusSocketFramer)
    connected = client.connect()
    if connected:
        # messagebox.showinfo("Connection Status", "Connected to Modbus server")
        update_Status()
        # Start the read_data thread only if connected and no thread is running
        if read_thread is None or not read_thread.is_alive():
            read_thread = threading.Thread(target=read_data)
            read_thread.start()
    else:
        # messagebox.showerror("Connection Status", "Failed to connect to Modbus server")
        update_Status()


read_thread = None
connect_to_modbus()
update_interface()
window.mainloop()
