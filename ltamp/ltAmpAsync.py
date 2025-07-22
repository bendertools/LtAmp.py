import os
import sys
import asyncio

from .ltAmpBase import LtAmpBase

# protobuf imports
protocol_path = os.path.join(os.path.dirname(__file__), 'protocol')
if protocol_path not in sys.path:
    sys.path.insert(0, protocol_path)

from .protocol import *

class LtAmpAsync(LtAmpBase):
    """
    async version of LtAmp controller using asyncio

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
         request_product_id()            get product ID
-
-    Data:
-        device                          Current HID device connection
-        hid_wrapper                     HID wrapper instance for backend operations
    """

    def __init__(self):
        super().__init__()
        self.loop = asyncio.get_event_loop()
        self._cs_event = asyncio.Event() # connection status
        self._fw_event = asyncio.Event() # firmware
        self._ps_event = asyncio.Event() # preset
        self._qa_event = asyncio.Event() # quick access
        self._aud_event = asyncio.Event() # audition
        self._mem_event = asyncio.Event() # memory
        self._pu_event = asyncio.Event() # processor
        self._ftsw_event = asyncio.Event() # footwitch
        self._gain_event = asyncio.Event() # usb gain

    async def connect(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, super().connect)

    async def disconnect(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, super().disconnect)

    async def request_connection_status(self):
        self._cs_event.clear()
        request_connection_status(self.device)
        try:
            await asyncio.wait_for(self._cs_event.wait(), timeout=self.timeout)
            return True
        except asyncio.TimeoutError:
           return False 

    async def request_current_preset(self):
        self._last_preset = None
        self._ps_event.clear()
        request_current_preset(self.device)
        try:
            await asyncio.wait_for(self._ps_event.wait(), timeout=self.timeout)
            return self._last_preset
        except asyncio.TimeoutError:
            raise TimeoutError("No current preset response received within timeout window.")

    async def request_firmware_version(self):
        self._last_firmware_version = None
        self._fw_event.clear()
        from .protocol import request_firmware_version
        request_firmware_version(self.device)
        try:
            await asyncio.wait_for(self._fw_event.wait(), timeout=self.timeout)
            return self._last_firmware_version
        except asyncio.TimeoutError:
            raise TimeoutError("No firmware version response received within timeout window.")

    async def request_qa_slots(self):
        self._last_qa_slots = None
        self._qa_event.clear()
        request_qa_slots(self.device)
        try:
            await asyncio.wait_for(self._qa_event.wait(), timeout=self.timeout)
            return self._last_qa_slots
        except asyncio.TimeoutError:
            raise TimeoutError("No QA slots response received within timeout window.")

    async def request_audition_state(self):
        self._last_audition_state = None
        self._aud_event.clear()
        request_audition_state(self.device)
        try:
            await asyncio.wait_for(self._aud_event.wait(), timeout=self.timeout)
            return self._last_audition_state
        except asyncio.TimeoutError:
            raise TimeoutError("No audition state response received within timeout window.") 

    async def request_memory_usage(self):
        self._last_memory_state = None
        self._mem_event.clear()
        request_memory_usage(self.device)
        try:
            await asyncio.wait_for(self._mem_event.wait(), timeout=self.timeout)
            return self._last_memory_state
        except asyncio.TimeoutError:
            raise TimeoutError("No memory state response received within timeout window.")

    async def request_processor_utilization(self):
        self._last_processor_utilization = None
        self._pu_event.clear()
        request_processor_utilization(self.device)
        try:
            await asyncio.wait_for(self._pu_event.wait(), timeout=self.timeout)
            return self._last_processor_utilization
        except asyncio.TimeoutError:
            raise TimeoutError("No processor utilization response received within timeout window.")

    async def request_usb_gain(self):
        self._last_gain_state = None
        self._gain_event.clear()
        request_usb_gain(self.device)
        try:
            await asyncio.wait_for(self._gain_event.wait(), timeout=self.timeout)
            return self._last_gain_state
        except asyncio.TimeoutError:
            raise TimeoutError("No usb gain state response received within timeout window.")

    async def request_product_id(self):
        self._last_product_id = None
        self._pid_event.clear()
        request_product_id(self.device)
        try:
            await asyncio.wait_for(self._pid_event.wait(), timeout=self.timeout)
            return self._last_product_id
        except asyncio.TimeoutError:
            raise TimeoutError("No product ID response received within timeout window.")
