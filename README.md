# lt25.py

[![PyPI Latest Release](https://img.shields.io/pypi/v/lt25.svg)](https://pypi.org/project/lt25/)
[![wakatime](https://wakatime.com/badge/user/7482ea9d-3085-4e9b-95ad-1ca78a14d948/project/08632cd5-4928-49fb-8d0d-2d8f2bebbdad.svg)](https://wakatime.com/badge/user/7482ea9d-3085-4e9b-95ad-1ca78a14d948/project/08632cd5-4928-49fb-8d0d-2d8f2bebbdad)
![MIT License](https://img.shields.io/github/license/bendertools/lt25.py)

🎸 A cross-platform Python module for interacting with the LT25 amplifier from a certain guitar company that rhymes with "bender" and names products after horses. 

## 👋 Introduction

I made this libray because I was disappointed by the lack of certain features in both my amp itself as well as the associated desktop app provided by its manufacturer. Failing to find a starting point which used modern languages/technologies I could build upon (.NET doesnt count), I developed this little module based on the reverse-engineering work others initiated.

### ⚙️ Specifications

This library requires Python 3.8+ to be installed on your system (due to demands of the protobuf 5 module). Additionally, the library only supports HID USB operations (no MIDI).

## 🚀 Quickstart

```
pip install lt25
```

> [!IMPORTANT]
> On linux, hidapi relies on libusb: `sudo apt install libusb-1.0-0-dev libudev-dev pkg-config`

## 💾 Usage

For full documentation of the LT25 and LT25Async classes, refer to the [wiki](/wiki). 

**Demonstration loop:**

> [!WARNING]
> On some linux distros, `sudo`-mode is required for running python files which interact with USB devices.


```python
import time
import lt25

amp = lt25.LT25()
amp.connect()
amp.send_sync_begin()
amp.send_sync_end()
amp.set_preset(5)
amp.set_qa_slots([1,2])
amp.request_firmware_version()
for i in range(5):
    amp.send_heartbeat()
    print(amp.request_qa_slots())
    time.sleep(1)
amp.disconnect()
```

## 🗺️ Roadmap

Compatibility with LtAmp protocol:

- [ ] Audio Status
- [x] Audition Preset (status, start, exit)
- [ ] Clear/rename/shift/swap/save (to/as) preset
- [ ] Connection Status
- [x] Current Preset (request/load)
- [ ] DSP Unit Parameter
- [x] Firmware Version
- [x] Heartbeat
- [ ] ⭐ LT4 Footswitch Mode 
- [ ] Loopback
- [x] Memory usage
- [x] Processor Utilization
- [x] QA Slots
- [x] Sync (Modal Status)
- [x] USB Gain

Other TODOs:
- [x] Publish to Pypi
- [x] Continuous Deployment
- [x] LT25Async/Base Classes
- [ ] Unit Testing
- [ ] Complete Protocol
- [ ] Other Amps

## 🛠️ Contributing

> [!NOTE]
> If you need to contribute in a way which updates protocol classes, you can find the original .proto files in Brent Maxwell's [repository](https://github.com/brentmaxwell/LtAmp/). I unfortunately cannot include these files in this module due to copyleft licensing restrictions.

lt25.py is licensed under the permissive MIT license, which means that you may fork, modify, adapt, and redistribute with few restrictions. If you wish to contribute your changes back to the base module, please open a [pull request](/pulls). To report bugs, request features, or discuss the project, open an [issue](/issues) or [discussion](/discussions).

## 🙌 Acknowledgements 

- Brent Maxwell ([@brentmaxwell](https://github.com/brentmaxwell)) and his LtAmp .NET libray: his published reverse engineering docs, schemas, proto files, etc. were instrumental in the creation of this Python module.
  - Additionally, some of the goals of his work greatly inspired those of this project.

