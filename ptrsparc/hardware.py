import logging,time,sys
from Queue import Queue
from threading import Thread,Event
#from multiprocessing import Pipe,Process,Event

from ftdi import FtdiChip
import messages
from messages import *
from config import *


logger = logging.getLogger(__name__)


READSIZE = 64 * 1024


class Hardware:
    master = None

    def __init__(self):
        logger.info("Searching for HiSPARC III Master...")
        master = self.get_master()
        if not master:
            raise RuntimeError("HiSPARC III Master not found")
        logger.info("Master found: %s" % master.serial)
        self.init_hardware(master)
        self.master = master
        self.master_buffer = bytearray()
        self.usbbuffer = Queue()
        self.config = Config(self)
        self.runswitch = Event()
        #self.usbgetter = Thread(target=self.read_data_into_buffer,args=())
        #self.usbprinter = Thread(target=self.print_message,args=())
        logger.info("HiSPARC III Master initialized")

    def get_master(self):
        serial = self.get_master_serial()
        if serial:
            return FtdiChip(serial)
        else:
            return None

    def get_master_serial(self):
        devices = FtdiChip.find_all()
        for device in devices:
            serial_str, description = device
            if description == "HiSPARC III Master":
                return serial_str
        return None

    def init_hardware(self, device):
        messages = [ResetMessage(True), InitializeMessage(False)]

        for message in messages:
            device.write(message.encode())

    def flush_and_get_measured_data_message(self):
        self.master.device.flushInput()
        while True:
            msg = self.read_message()
            if type(msg) == messages.MeasuredDataMessage:
                break
        return msg

    def read_message(self):
        try:#TODO: aanpassuhhhh!
            input_buff = self.master.read(READSIZE)
            self.master_buffer.extend(input_buff)
        finally:
            return HisparcMessageFactory(self.master_buffer)
    
    def print_message(self):
        lastpps = 0
        #while (not self.runswitch.is_set()):
        while True:
            millis = int(round(time.time() * 1000))
            msg = self.flush_and_get_measured_data_message()
            logger.info((msg.count_ticks_PPS-lastpps)/1000)
            lastpps = msg.count_ticks_PPS
            #logger.info(msg)
            #sys.stdout.write(msg.get_raw_msg())
            #logger.info(str(n(msg.get_raw_msg())))
            millis = int(round(time.time() * 1000))-millis
            #logger.info("hisparc took "+str(millis)+"ms")
    
    def queue_to_array(self):
        while not self.usbbuffer.empty():
            input_buff = self.usbbuffer.get_nowait()
            self.master_buffer.extend(input_buff)

    def read_data_into_buffer(self):
        buffsizecounter = 0
        input_buff = self.master.read(READSIZE)
        self.usbbuffer.put(input_buff)
        while (not self.runswitch.is_set()):
            input_buff = self.master.read(READSIZE)
            self.usbbuffer.put(input_buff)

    def send_message(self, msg):
        self.master.write(msg.encode())

    def flush_buffer(self):
        while True:
            msg = self.read_message()
            if msg is None:
                break

    def close(self):
        if self.master:
            self.runswitch.clear()
            self.master.write(ResetMessage(True).encode())
            time.sleep(1)
            self.master.flush_input()
            self.master.close()
        self._closed = True

    def __del__(self):
        if not self.__dict__.get('_closed'):
            self.close()
            
#####################################
## Brent
#####################################

    def start_run(self):
        self.runswitch.clear()
        self.usbgetter.start()
        logger.info("Started taking data.")
    
    def stop_run(self):
        self.runswitch.set()
        self.usbgetter.join()
        logger.info("Stopped taking data.")
        
    def start_raw_run(self):
        self.runswitch.clear()
        #self.usbprinter.start()
        logger.info("Started taking data, raw mode.")
        self.send_message(messages.TriggerConditionMessage(0x40))
        self.print_message()
    
    def stop_raw_run(self):
        self.runswitch.set()
        self.usbprinter.join()
        logger.info("Stopped taking data, raw mode.")
