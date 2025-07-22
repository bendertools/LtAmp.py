import time
import threading
import platform
import sys
import os

from .hidWrapper import HIDWrapper, HIDDevice

# protobuf imports
protocol_path = os.path.join(os.path.dirname(__file__), 'protocol')
if protocol_path not in sys.path:
    sys.path.insert(0, protocol_path)

from .protocol import *

VENDOR_ID = 0x1ed8
PRODUCT_ID = 0x0037

class LtAmpBase:
    """
    base class for LT amplifier communication
    """
    def __init__(self, debug=False, timeout=2.0):
        self.debug = debug
        self.timeout = timeout
        self.hid_wrapper = HIDWrapper(self.debug)
        self.device = None
        self._msg_buffer = bytearray()
        self._stop_event = threading.Event()
        self._cs_event = threading.Event() # connection status
        self._fw_event = threading.Event() # firmware
        self._ps_event = threading.Event() # preset
        self._qa_event = threading.Event() # quick access
        self._aud_event = threading.Event() # audition
        self._mem_event = threading.Event() # memory
        self._pu_event = threading.Event() # processor
        self._ftsw_event = threading.Event() # footswitch
        self._gain_event = threading.Event() # usb gain
        self._pid_event = threading.Event() # product ID

    def _set_event(self, event):
        if hasattr(self, 'loop') and self.loop is not None:
            self.loop.call_soon_threadsafe(event.set)
        else:
            event.set()

    def find_amp(self):
        devices = self.hid_wrapper.enumerate(VENDOR_ID, PRODUCT_ID)
        if devices:
            return devices[0]
        return None

    def connect(self):
        amp_info = self.find_amp()
        if not amp_info:
            raise RuntimeError("LT amp not found")
        self.device = self.hid_wrapper.open_device(amp_info)
        self.device.set_input_callback(self._process_input_data)
        if self.hid_wrapper.backend == "hidapi":
            self._input_thread = threading.Thread(target=self._input_thread_proc, daemon=True)
            self._input_thread.start()
        return True

    def disconnect(self):
        self._stop_event.set()
        if self.device:
            self.device.close()

    def _input_thread_proc(self):
        while not self._stop_event.is_set():
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
                return
            if self.hid_wrapper.backend == "hidapi":
                offset = 1 if data_list[0] == 0x00 else 0
                if len(data_list) < offset + 3:
                    return
                tag = data_list[offset]
                length = data_list[offset + 1]
                value = data_list[offset + 2:offset + 2 + length]
            else:  # pywinusb
                tag = data_list[2]
                length = data_list[3]
                value = data_list[4:4 + length] 
            if tag == 0x33:
                self._msg_buffer = bytearray(value)
            elif tag == 0x34:
                self._msg_buffer += bytearray(value)
            elif tag == 0x35:
                self._msg_buffer += bytearray(value)
                try:
                    msg = FenderMessageLT()
                    msg.ParseFromString(self._msg_buffer)

                    if self.debug:
                        print("====== DEBUG =====\r\n", msg)

                    if msg.HasField("connectionStatus"):
                        status = msg.connectionStatus.isConnected
                        self._set_event(self._cs_event)
                    elif msg.HasField("currentPresetStatus"):
                        preset_json = msg.currentPresetStatus.currentPresetData
                        preset_index = msg.currentPresetStatus.currentSlotIndex
                        self._last_preset = {"data": preset_json, "index": preset_index}
                        self._set_event(self._ps_event)
                    elif msg.HasField("firmwareVersionStatus"):
                        version = msg.firmwareVersionStatus.version
                        self._last_firmware_version = version
                        self._set_event(self._fw_event)
                    elif msg.HasField("qASlotsStatus"):
                        slots = msg.qASlotsStatus
                        self._last_qa_slots = list(slots.slots)
                        self._set_event(self._qa_event)
                    elif msg.HasField("auditionStateStatus"):
                        state = msg.auditionStateStatus.isAuditioning
                        self._last_audition_state = state
                        self._set_event(self._aud_event)
                    elif msg.HasField("memoryUsageStatus"):
                        memory_state = msg.memoryUsageStatus
                        self._last_memory_state = {"stack": memory_state.stack, "heap": memory_state.heap}
                        self._set_event(self._mem_event)
                    elif msg.HasField("lt4FootswitchModeStatus"):
                        mode = msg.lt4FootswitchModeStatus.mode
                        self._last_ftsw_state = mode
                        self._set_event(self._ftsw_event)
                    elif msg.HasField("usbGainStatus"):
                        gain = msg.usbGainStatus.valueDB
                        self._last_gain_state = gain
                        self._set_event(self._gain_event)
                    elif msg.HasField("processorUtilization"):
                        utilization = msg.processorUtilization
                        self._last_processor_utilization = {
                            "percent": utilization.percent,
                            "minPercent": utilization.minPercent,
                            "maxPercent": utilization.maxPercent
                        }
                        self._set_event(self._pu_event)
                    elif msg.HasField("productIdentificationStatus"):
                        pid = msg.productIdentificationStatus.id
                        self._last_product_id = pid
                        self._set_event(self._pid_event)
                except Exception:
                    pass
                self._msg_buffer = bytearray()
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

    def set_qa_slots(self, slots: list):
        if not isinstance(slots, list) or len(slots) != 2:
            raise ValueError("QA slots must be a list of exactly 2 preset indices.")
        set_qa_slots(self.device, slots)

    def audition_preset(self, preset_json: str):
        if not isinstance(preset_json, str):
            raise ValueError("Preset JSON must be a string.")
        audition_preset(self.device, preset_json)

    def exit_audition(self):
        exit_audition(self.device)

    def set_usb_gain(self, gain: float):
        if not isinstance(gain, float) or not (-15.0 <= gain <= 15.0):
            raise ValueError("USB gain must be a float between -15.0<dB<15.0.")
        set_usb_gain(self.device, gain)
