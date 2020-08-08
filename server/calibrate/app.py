from tkinter import Tk, Label, Button, Entry, IntVar, END, W, E
from mqtt.mqtt_setup import *

class HoneyPiCalibrator:
    def __init__(self, master):
        # Setup the MQTT client
        self.mqtt_client = mqtt_setup()

        self.master = master
        master.title("Honey-Pi Calibration")

        # Static text on GUI
        self.pallet_number_label = Label(master,text="Pallet Number")
        self.hive_number_label = Label(master,text="Hive Number")
        self.cal_weight_label = Label(master, text="Calibration Weight (kg)")

        # Input entry fields
        vcmd = master.register(self.validate) # we have to wrap the command
        self.pallet_number_entry = Entry(master, validate="key", validatecommand=(vcmd, '%P'))
        self.hive_number_entry = Entry(master, validate="key", validatecommand=(vcmd, '%P'))
        self.cal_weight_entry = Entry(master, validate="key", validatecommand=(vcmd, '%P'))

        # Buttons on the GUI
        self.tare_button = Button(master, text="Tare", command=lambda: self.tare())
        self.calibrate_button = Button(master, text="Calibrate", command=lambda: self.calibrate())

        # Layout
        # Row 0
        self.pallet_number_label.grid(row=0, column=0)
        self.hive_number_label.grid(row=0, column=1)

        # Row 1
        self.pallet_number_entry.grid(row=1, column=0, sticky=W)
        self.hive_number_entry.grid(row=1, column=1, sticky=W)

        # Row 2
        self.cal_weight_label.grid(row=2, column=0, columnspan=2)
        self.cal_weight_entry.grid(row=3, column=0, columnspan=2)

        # Row 3
        self.tare_button.grid(row=4, column=0)
        self.calibrate_button.grid(row=4, column=1)

    def tare(self):
        """
        Send a tare command to the hive
        """
        pallet_number = self.pallet_number_entry.get()
        hive_number = self.hive_number_entry.get()
        self.mqtt_client.publish(topic="honey_pi/pallet/" + str(pallet_number) +"/hive/" + hive_number + "/calibrate/tare",payload="0")

    def calibrate(self):
        """
        Calibrate the scale to a known weight in KG
        """
        pallet_number = self.pallet_number_entry.get()
        hive_number = self.hive_number_entry.get()
        calibrated_weight = self.cal_weight_entry.get()
        self.mqtt_client.publish(topic="honey_pi/pallet/" + str(pallet_number) +"/hive/" + hive_number + "/calibrate/weight",payload=hive_number +","+calibrated_weight)

    def validate(self, new_text):
        # Ensure the entry is a number
        if not new_text: # the field is being cleared
            return True
        try:
            return True
        except ValueError:
            return False


if __name__ == '__main__':
    root = Tk()
    my_gui = HoneyPiCalibrator(root)
    root.mainloop()

