import time
import threading
import platform
import sys
import os

from .hidwrapper import HIDWrapper, HIDDevice, HIDBackendNotFound

# Protobuf imports - these must be generated from the official .proto files!
protocol_path = os.path.join(os.path.dirname(__file__), 'protocol')
if protocol_path not in sys.path:
    sys.path.insert(0, protocol_path)

from .protocol import *

# lt25 amp constants
VENDOR_ID = 0x1ed8
PRODUCT_ID = 0x0037

class LT25:
    """
    main user-facing class to control the LT25 amp via USB.

    Methods:
        connect()                       connects to the amp (finds first matching device)
        disconnect()                    disconnect and clean up
        send_sync_begin()               send SYNC_BEGIN (start handshake)
        send_sync_end()                 send SYNC_END (end handshake)
        send_heartbeat()                periodic heartbeat (keep-alive)
        request_firmware_version()      request firmware version from amp
        set_preset(idx)                 change preset slot
        request_current_preset()        ask amp for current preset (status event)
        set_qa_slots(idx[])             set QA slots (footswitch assignments)
        request_qa_slots()              request QA slots from amp (status event)
        audition_preset(preset_json)    audition a preset
        exit_audition()                 exit audition mode
        request_audition_state()        get current audition state (status event)
        request_memory_usage()          get memory usage
        request_processor_utilization() get processor utilization
        request_footswitch_mode()       get current footswitch mode
        set_usb_gain(gain)              set USB gain (0-100)
        request_usb_gain()              get current USB gain setting

    Data:
        last_message                    Last parsed message
        device                          Current HID device connection
        hid_wrapper                     HID wrapper instance for backend operations
    """
    def __init__(self):
        self.hid_wrapper = HIDWrapper()
        self.device = None
        self.msg_buffer = bytearray()
        self.stop_event = threading.Event()
        self.last_message = None
        self._input_thread = None
        self._fw_event = threading.Event()
        self._ps_event = threading.Event()
        self._qa_event = threading.Event()
        self._aud_event = threading.Event()
        self._mem_event = threading.Event()
        self._pu_event = threading.Event()
        self._ftsw_event = threading.Event()
        self._gain_event = threading.Event()

    def find_amp(self):
        devices = self.hid_wrapper.enumerate(VENDOR_ID, PRODUCT_ID)
        if devices:
            return devices[0]
        return None

    def connect(self):
        amp_info = self.find_amp()
        if not amp_info:
            raise RuntimeError("Fender LT25 not found")
        self.device = self.hid_wrapper.open_device(amp_info)
        self.device.set_input_callback(self._process_input_data)
        if self.hid_wrapper.backend == "hidapi":
            self._input_thread = threading.Thread(target=self._input_thread_proc, daemon=True)
            self._input_thread.start()
        return True

    def disconnect(self):
        self.stop_event.set()
        if self.device:
            self.device.close()

    def _input_thread_proc(self):
        while not self.stop_event.is_set():
            try:
                data = self.device.read(64, 100)
                if data and any(b != 0 for b in data):
                    self._process_input_data(data)
            except Exception:
                time.sleep(0.1)

    def _process_input_data(self, data):
        try:
            data_list = list(data)
            
            if len(data_list) < 4:
                # ignoring data which is too short
                return
            
            if self.hid_wrapper.backend == "hidapi":
                offset = 1 if data_list[0] == 0x00 else 0
                if len(data_list) < offset + 3:
                    return
                    
                tag = data_list[offset]
                length = data_list[offset + 1]
                value = data_list[offset + 2:offset + 2 + length]
            else: #pywinusb
                tag = data_list[2]
                length = data_list[3]
                value = data_list[4:4 + length] 
            
            # handle multiple packets
            if tag == 0x33:
                self.msg_buffer = bytearray(value)
            elif tag == 0x34:
                self.msg_buffer += bytearray(value)
            elif tag == 0x35:
                self.msg_buffer += bytearray(value)
                try:
                    msg = FenderMessageLT()
                    msg.ParseFromString(self.msg_buffer)

                    # Debugging/testing new messages
                    # print(f"Received message: {msg}")
 
                    # handle different types of responses
                    if msg.HasField("currentPresetStatus"):
                        preset_json = msg.currentPresetStatus.currentPresetData
                        preset_index = msg.currentPresetStatus.currentSlotIndex
                        self._last_preset = { "data": preset_json, "index": preset_index }
                        self._ps_event.set()
                    elif msg.HasField("firmwareVersionStatus"):
                        version = msg.firmwareVersionStatus.version
                        self._last_firmware_version = version
                        self._fw_event.set()
                    elif msg.HasField("qASlotsStatus"):
                        slots = msg.qASlotsStatus
                        self._last_qa_slots = list(slots.slots)
                        self._qa_event.set()
                    elif msg.HasField("auditionStateStatus"):
                        state = msg.auditionStateStatus.isAuditioning
                        self._last_audition_state = state
                        self._aud_event.set()
                    elif msg.HasField("memoryUsageStatus"):
                        memory_state = msg.memoryUsageStatus
                        self._last_memory_state = {"stack": memory_state.stack, "heap": memory_state.heap}
                        self._mem_event.set()
                    elif msg.HasField("lt4FootswitchModeStatus"):
                        mode = msg.lt4FootswitchModeStatus.mode
                        self._last_ftsw_state = mode
                        self._ftsw_event.set()
                    elif msg.HasField("usbGainStatus"):
                        gain = msg.usbGainStatus.valueDB
                        self._last_gain_state = gain
                        self._gain_event.set()
                    elif msg.HasField("processorUtilization"):
                        utilization = msg.processorUtilization
                        self._last_processor_utilization = { "percent": utilization.percent, "minPercent": utilization.minPercent, "maxPercent": utilization.maxPercent }
                        self._pu_event.set()
                       
                except Exception as e:
                    pass
                    
                self.msg_buffer = bytearray()
                                    
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            raise RuntimeError(f"Error processing input data: {e}\n{tb}")

    def send_message(self, msg):
        send_message(self.device, msg)

    def send_heartbeat(self):
        send_heartbeat(self.device)

    def send_sync_begin(self):
        send_sync_begin(self.device)

    def send_sync_end(self):
        send_sync_end(self.device)

    def set_preset(self, preset_index: int):
        if not isinstance(preset_index, int) or preset_index < 0:
            raise ValueError("Preset index must be a non-negative integer.")
        set_preset(self.device, preset_index)

    def request_current_preset(self):
        """returns dict of preset info: {'index': int, 'data': str} """
        self._last_preset = None
        self._ps_event.clear()
        request_current_preset(self.device)
        if self._ps_event.wait(timeout=2.0):
            return self._last_preset
        else:
            raise TimeoutError("No current preset response received.")

    def request_firmware_version(self):
        self._last_firmware_version = None
        self._fw_event.clear()
        from .protocol import request_firmware_version
        request_firmware_version(self.device)
        if self._fw_event.wait(timeout=2.0):
            return self._last_firmware_version
        else:
            raise TimeoutError("No firmware version response received.")

    def set_qa_slots(self, slots: List[int]):
        if not isinstance(slots, list) or len(slots) != 2:
            raise ValueError("QA slots must be a list of exactly 2 preset indices.")
        set_qa_slots(self.device, slots)

    def request_qa_slots(self):
        """returns list of QA slots integers (length 2)"""
        self._last_qa_slots = None
        self._qa_event.clear()
        request_qa_slots(self.device)
        if self._qa_event.wait(timeout=5.0):
            return self._last_qa_slots
        else:
            raise TimeoutError("No QA slots response received.")

    def audition_preset(self, preset_json: str):
        if not isinstance(preset_json, str):
            raise ValueError("Preset JSON must be a string.")
        audition_preset(self.device, preset_json)

    def exit_audition(self):
        exit_audition(self.device)

    def request_audition_state(self):
        self._last_audition_state = None
        self._aud_event.clear()
        request_audition_state(self.device)
        if self._aud_event.wait(timeout=2.0):
            return self._last_audition_state
        else:
            raise TimeoutError("No audition state response received.") 

    def request_memory_usage(self):
        """returns dict with memory usage: {'stack': int, 'heap': int}"""
        self._last_memory_state = None
        self._mem_event.clear()
        request_memory_usage(self.device)
        if self._mem_event.wait(timeout=2.0):
            return self._last_memory_state
        else:
            raise TimeoutError("No memory state response received.")

    def request_processor_utilization(self):
        """returns dict with processor utilization: {'percent': float, 'minPercent': float, 'maxPercent': float}"""
        self._last_processor_utilization = None
        self._pu_event.clear()
        request_processor_utilization(self.device)
        if self._pu_event.wait(timeout=2.0):
            return self._last_processor_utilization
        else:
            raise TimeoutError("No processor utilization response received.")
       
    def set_usb_gain(self, gain: float):
        if not isinstance(gain, float) or not (-15.0 <= gain <= 15.0):
            raise ValueError("USB gain must be a float between -15.0<dB<15.0.")
        set_usb_gain(self.device, gain)

    def request_usb_gain(self):
        self._last_gain_state = None
        self._gain_event.clear()
        request_usb_gain(self.device)
        if self._gain_event.wait(timeout=2.0):
            return self._last_gain_state
        else:
            raise TimeoutError("No usb gain state response received.")

