class HIDDevice:
    """unified HID device interface"""
    
    def __init__(self, device, backend, debug=False):
        self.device = device
        self.backend = backend
        self.debug = debug
        self.input_callback = None

    def write(self, data):
        """write data to device"""
        if self.backend == "hidapi":
            # plain data but pad to 64 bytes
            packet = bytearray(64)
            for i in range(min(len(data), 64)):
                packet[i] = data[i]
            
            result = self.device.write(packet)
        elif self.backend == "pywinusb":
            # needs 65 bytes: [report_id] + [64 bytes of data]
            packet = bytearray(65)
            packet[0] = 0x00 
            for i in range(min(len(data), 64)):
                packet[i + 1] = data[i]
            
            out_report = self.device.find_output_reports()[0]
            out_report.set_raw_data(packet)
            out_report.send()

    def read(self, length=64, timeout_ms=100):
        """read data from device (hidapi only)"""
        if self.backend == "hidapi":
            try:
                data = self.device.read(length, timeout_ms)
                return bytes(data) if data else None
            except Exception as e:
                raise RuntimeError(f"Failed to read from device: {e}") 
        elif self.backend == "pywinusb":
            return None
    
    def set_input_callback(self, callback):
        """set callback for inputted data"""
        self.input_callback = callback
        if self.backend == "pywinusb":
            self.device.set_raw_data_handler(self._pywinusb_callback)
    
    def _pywinusb_callback(self, data):
        """internal callback adapter for pywinusb"""
        if self.input_callback:
            data_list = list(data)
            if len(data_list) >= 4:
                converted = data_list[0:]
                self.input_callback(bytes(converted))
    
    def close(self):
        """close device"""
        try:
            self.device.close()
        except:
            pass

