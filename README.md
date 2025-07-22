# LtAmp.py

[![PyPI Latest Release](https://img.shields.io/pypi/v/ltamp.svg)](https://pypi.org/project/ltamp/)
[![wakatime](https://wakatime.com/badge/user/7482ea9d-3085-4e9b-95ad-1ca78a14d948/project/08632cd5-4928-49fb-8d0d-2d8f2bebbdad.svg)](https://wakatime.com/badge/user/7482ea9d-3085-4e9b-95ad-1ca78a14d948/project/08632cd5-4928-49fb-8d0d-2d8f2bebbdad)
![MIT License](https://img.shields.io/github/license/bendertools/ltamp.py)

🎸 A cross-platform Python module for interacting with the LT amplifiers from a certain guitar company that rhymes with "bender" and names products after horses.

> [!NOTE]
> At the moment, only LT25 amps are fully tested and have been tested/verified for protocol support.

## 👋 Introduction

I made this libray because I was disappointed by the lack of certain features in both my amp itself as well as the associated desktop app provided by its manufacturer. Failing to find a starting point which used modern languages/technologies I could build upon (.NET doesnt count), I developed this little module based on the reverse-engineering work others initiated.

### ⚙️ Specifications

This package requires Python 3.8+ to be installed on your system (due to demands of the protobuf 5 module). Additionally, the library only supports HID USB operations (no MIDI).

## 🚀 Quickstart

```
pip install ltamp
python
>>> from ltamp import LtAmp
>>> LtAmp().connect()
```

> [!IMPORTANT]
> On linux, hidapi relies on libusb: `sudo apt install libusb-1.0-0-dev libudev-dev pkg-config`

## 💾 Usage

For full documentation of the LtAmp and LtAmpAsync classes, refer to the [wiki](/wiki).

**Demonstration loop:**

```python
import time
import ltamp

amp = ltamp.LtAmp()
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

> [!WARNING]
> On some linux distros, `sudo`-mode is required for running python files which interact with USB devices.

## 🗺️ Roadmap

Compatibility with LtAmp protocol:

- [ ] Audio Status
- [x] Audition Preset (status, start, exit)
- [ ] Clear/rename/shift/swap/save (to/as) preset
- [x] Connection Status
- [x] Current Preset (request/load)
- [ ] DSP Unit Parameter
- [x] Firmware Version
- [x] Heartbeat
- [x] LT4 Footswitch Mode
- [ ] Loopback
- [x] Memory usage
- [x] Product Identification
- [x] Processor Utilization
- [x] QA Slots
- [x] Sync (Modal Status)
- [x] USB Gain

Other TODOs:

- [x] Publish to Pypi
- [x] Continuous Deployment
- [x] LtAmpAsync/Base Classes
- [x] Document classes in Wiki
- [ ] Unit Testing
- [x] Customize timeout
- [ ] Complete Protocol
- [x] Other LT Amps
- [ ] Multiple Connected Devices

Fully-tested LT-series amps:

- [x] LT25
- [ ] LT40S
- [ ] LT50
- [ ] LTX100?
- [ ] LTX50?
- [ ] R15-R100?

## 🛠️ Contributing

> [!NOTE]
> If you need to contribute in a way which updates protocol classes, you can find the original .proto files in Brent Maxwell's [repository](https://github.com/brentmaxwell/LtAmp/). I unfortunately cannot include these files in this module due to copyleft licensing restrictions.

LtAmp.py is licensed under the permissive MIT license, which means that you may fork, modify, adapt, and redistribute with few restrictions. If you wish to contribute your changes back to the base module, please open a [pull request](/pulls). To report bugs, request features, or discuss the project, open an [issue](/issues) or [discussion](/discussions).

## 🙌 Acknowledgements

- Brent Maxwell ([@brentmaxwell](https://github.com/brentmaxwell)) and his LtAmp .NET libray: his published reverse engineering docs, schemas, proto files, etc. were instrumental in the creation of this Python module.
  - Additionally, some of the goals of his work greatly inspired those of this project.
