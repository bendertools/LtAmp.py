import os
import sys

from .ltAmpBase import LtAmpBase

# protobuf imports
protocol_path = os.path.join(os.path.dirname(__file__), 'protocol')
if protocol_path not in sys.path:
    sys.path.insert(0, protocol_path)

from .protocol import *

class LtAmp(LtAmpBase):
    """
    synchronous version of LT amp controller

    Methods:
-        connect()                       connects to the amp (first matching device)
-        disconnect()                    disconnect and clean up
-        send_sync_begin()               send SYNC_BEGIN (start handshake)
-        send_sync_end()                 send SYNC_END (end handshake)
-        send_heartbeat()                periodic heartbeat (keep-alive)
         request_connection_status()     request connection status (status event)
-        request_firmware_version()      request firmware version from amp
-        set_preset(idx)                 change preset slot
-        request_current_preset()        ask amp for current preset (status event)
-        set_qa_slots(idx[])             set QA slots (footswitch assignments)
-        request_qa_slots()              request QA slots from amp (status event)
-        audition_preset(preset_json)    audition a preset
-        exit_audition()                 exit audition mode
-        request_audition_state()        get current audition state (status event)
-        request_memory_usage()          get memory usage
-        request_processor_utilization() get processor utilization
-        request_footswitch_mode()       get current footswitch mode (lt4 only!)
-        set_usb_gain(gain)              set USB gain (0-100)
-        request_usb_gain()              get current USB gain setting
-        request_product_id()            get product ID
-
-    Data:
-        device                          Current HID device connection
-        hid_wrapper                     HID wrapper instance for backend operations
    """

    def request_connection_status(self):
        self._cs_event.clear()
        request_connection_status(self.device)
        if self._cs_event.wait(timeout=self.timeout):
            return True
        else:
            return False

    def request_current_preset(self):
        self._last_preset = None
        self._ps_event.clear()
        request_current_preset(self.device)
        if self._ps_event.wait(timeout=self.timeout):
            return self._last_preset
        else:
            raise TimeoutError("No current preset response received within timeout window.")

    def request_firmware_version(self):
        self._last_firmware_version = None
        self._fw_event.clear()
        from .protocol import request_firmware_version
        request_firmware_version(self.device)
        if self._fw_event.wait(timeout=self.timeout):
            return self._last_firmware_version
        else:
            raise TimeoutError("No firmware version response received within timeout window.")

    def request_qa_slots(self):
        self._last_qa_slots = None
        self._qa_event.clear()
        request_qa_slots(self.device)
        if self._qa_event.wait(timeout=self.timeout):
            return self._last_qa_slots
        else:
            raise TimeoutError("No QA slots response received within timeout window.")

    def request_audition_state(self):
        self._last_audition_state = None
        self._aud_event.clear()
        request_audition_state(self.device)
        if self._aud_event.wait(timeout=self.timeout):
            return self._last_audition_state
        else:
            raise TimeoutError("No audition state response received within timeout window.") 

    def request_memory_usage(self):
        self._last_memory_state = None
        self._mem_event.clear()
        request_memory_usage(self.device)
        if self._mem_event.wait(timeout=self.timeout):
            return self._last_memory_state
        else:
            raise TimeoutError("No memory state response received within timeout window.")

    def request_processor_utilization(self):
        self._last_processor_utilization = None
        self._pu_event.clear()
        request_processor_utilization(self.device)
        if self._pu_event.wait(timeout=self.timeout):
            return self._last_processor_utilization
        else:
            raise TimeoutError("No processor utilization response received within timeout window.")

    def request_usb_gain(self):
        self._last_gain_state = None
        self._gain_event.clear()
        request_usb_gain(self.device)
        if self._gain_event.wait(timeout=self.timeout):
            return self._last_gain_state
        else:
            raise TimeoutError("No usb gain state response received within timeout window.")

    def request_footswitch_mode(self):
        self._last_ftsw_state = None
        self._ftsw_event.clear()
        request_footswitch_mode(self.device)
        if self._ftsw_event.wait(timeout=self.timeout):
            return self._last_ftsw_state
        else:
            raise TimeoutError("No footswitch mode response received within timeout window. (Maybe not an LT4?)")

    def request_product_id(self):
        self._last_product_id = None
        self._pid_event.clear()
        request_product_id(self.device)
        if self._pid_event.wait(timeout=self.timeout):
            return self._last_product_id
        else:
            raise TimeoutError("No product ID response received within timeout window.")
