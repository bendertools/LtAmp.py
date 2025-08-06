import unittest
import time
from ltamp import LtAmp
import threading

class TestLtAmp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.amp = LtAmp()
        try:
            cls.amp.connect()
            cls.amp.send_sync_begin()
            time.sleep(1)
            cls.amp.send_heartbeat()
            cls.amp.send_sync_end()
            cls._heartbeat_running = True
            def heartbeat():
                while cls._heartbeat_running:
                    cls.amp.send_heartbeat()
                    time.sleep(0.1)
            cls._heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
            cls._heartbeat_thread.start()
        except Exception as e:
            cls.amp = None
            print(f"SKIPPING tests: Could not connect to amp: {e}")

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, "amp", None):
            cls._heartbeat_running = False
            cls._heartbeat_thread.join(timeout=2)
            cls.amp.disconnect()

    def setUp(self):
        if self.amp is None:
            self.skipTest("Amp not connected, skipping hardware integration tests.")

    def test_firmware_version(self):
        version = self.amp.request_firmware_version()
        self.assertIsInstance(version, str)
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")

    def test_product_id(self):
        pid = self.amp.request_product_id()
        self.assertIsInstance(pid, str)

    def test_qa_slots(self):
        slots = self.amp.request_qa_slots()
        self.assertIsInstance(slots, list)
        self.assertEqual(len(slots), 2)
        self.assertTrue(all(isinstance(x, int) for x in slots))

    def test_set_and_get_preset(self):
        orig_preset = self.amp.request_current_preset()
        idx = orig_preset["index"]
        self.amp.set_preset(idx)
        time.sleep(1)
        curr = self.amp.request_current_preset()
        self.assertEqual(curr["index"], idx)

    def test_usb_gain(self):
        orig_gain = self.amp.request_usb_gain()
        self.amp.set_usb_gain(orig_gain)
        time.sleep(0.5)
        gain = self.amp.request_usb_gain()
        self.assertEqual(gain, orig_gain)

    
    def test_memory_usage(self):
        mem = self.amp.request_memory_usage()
        self.assertIsInstance(mem, dict)
        self.assertIn("stack", mem)
        self.assertIn("heap", mem)
        self.assertIsInstance(mem["stack"], int)
        self.assertIsInstance(mem["heap"], int)

    def test_processor_utilization(self):
        util = self.amp.request_processor_utilization()
        self.assertIsInstance(util, dict)
        for key in ("percent", "minPercent", "maxPercent"):
            self.assertIn(key, util)
            self.assertIsInstance(util[key], float)
            self.assertGreaterEqual(util[key], 0)

    def test_send_sync_begin_end(self):
        # Just ensure both calls do not raise
        try:
            self.amp.send_sync_begin()
            time.sleep(1)
            self.amp.send_sync_end()
        except Exception as e:
           self.fail(f"send_sync_begin() or send_sync_end() raised an exception: {e}")

    def test_disconnect(self):
        try:
            self.amp.disconnect()
        except Exception as e:
            self.fail(f"disconnect() raised an exception: {e}")
        # Reconnect for further tests (if needed)
        try:
            self.amp.connect()
            self.amp.send_sync_begin()
            time.sleep(1)
            self.amp.send_sync_end()
        except Exception as e:
            self.skipTest(f"Could not reconnect to amp after disconnect: {e}")

if __name__ == "__main__":
    unittest.main()
