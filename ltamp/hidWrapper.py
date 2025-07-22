import platform

from .hidDevice import HIDDevice

class HIDWrapper:
    """unified HID interface that works across platforms"""
    
    def __init__(self, debug=False):
        self.backend = None
        self.hid_lib = None
        self.debug = False
        self._setup_hid_library()
    
    def _setup_hid_library(self):
        """detect and setup the best available HID library"""
        try:
            import hid
            self.hid_lib = hid
            self.backend = "hidapi"
            return
        except ImportError:
            pass
              
        if platform.system() == "Windows":
            try:
                from pywinusb import hid as pywinusb_hid
                self.hid_lib = pywinusb_hid
                self.backend = "pywinusb"
                return
            except ImportError:
                pass
        
        raise ImportError("No HID library found. Please install hidapi or pywinusb")
    
    def enumerate(self, vendor_id=None, product_id=None):
        """enumerate HID devices"""
        if self.backend == "hidapi":
            if vendor_id and product_id:
                return self.hid_lib.enumerate(vendor_id, product_id)
            else:
                return self.hid_lib.enumerate()
        elif self.backend == "pywinusb":
            devices = self.hid_lib.find_all_hid_devices()
            if vendor_id and product_id:
                return [d for d in devices if d.vendor_id == vendor_id and d.product_id == product_id]
            return devices
    
    def open_device(self, device_info):
        """open and return an HID device"""
        if self.backend == "hidapi":
            device = self.hid_lib.device()
            device.open_path(device_info['path'])
            return HIDDevice(device, self.backend, debug=self.debug)
        elif self.backend == "pywinusb":
            device_info.open()
            return HIDDevice(device_info, self.backend, debug=self.debug)
