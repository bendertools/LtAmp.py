"""
protocol actions for LT25 USB control.

covers QA, firmware, preset status, auditioning,
memory, footswitch status, USB gain.
"""

from typing import List

from .FenderMessageLT_pb2 import FenderMessageLT, ResponseType
from .Heartbeat_pb2 import Heartbeat
from .ModalStatusMessage_pb2 import ModalContext, ModalStatusMessage, ModalState
from .FirmwareVersionRequest_pb2 import FirmwareVersionRequest
from .LoadPreset_pb2 import LoadPreset
from .UsbGainSet_pb2 import UsbGainSet
from .QASlotsRequest_pb2 import QASlotsRequest
from .QASlotsSet_pb2 import QASlotsSet
from .CurrentPresetRequest_pb2 import CurrentPresetRequest
from .AuditionPreset_pb2 import AuditionPreset
from .LoadPreset_pb2 import LoadPreset
from .AuditionStateRequest_pb2 import AuditionStateRequest
from .ExitAuditionPreset_pb2 import ExitAuditionPreset
from .MemoryUsageRequest_pb2 import MemoryUsageRequest
from .ProcessorUtilizationRequest_pb2 import ProcessorUtilizationRequest
from .LT4FootswitchModeRequest_pb2 import LT4FootswitchModeRequest
from .UsbGainRequest_pb2 import UsbGainRequest

def send_message(device, msg):
    """
    send (potentially multi-packet) protobuf message
    """
    payload = msg.SerializeToString()
    max_chunk = 61 # max payload per packet

    if len(payload) <= max_chunk:
        # single packet
        tag = 0x35
        length = len(payload)
        packet = bytearray([tag, length]) + payload
        if len(packet) < 64: # pad to 64
            packet.extend([0x00] * (64 - len(packet)))
        device.write(packet)
    else:
        # multiple packets
        num_chunks = (len(payload) + max_chunk - 1) // max_chunk
        for i in range(num_chunks):
            start = i * max_chunk
            end = min(len(payload), (i + 1) * max_chunk)
            chunk = payload[start:end]
            if i == 0:
                tag = 0x33  # start
            elif i == num_chunks - 1:
                tag = 0x35  # end
            else:
                tag = 0x34  # middle
            length = len(chunk)
            packet = bytearray([tag, length]) + chunk
            if len(packet) < 64:
                packet.extend([0x00] * (64 - len(packet)))
            device.write(packet)


def _msg(**kwargs):
    """construct a FenderMessageLT with given fields"""
    msg = FenderMessageLT()
    msg.responseType = ResponseType.UNSOLICITED
    for k, v in kwargs.items():
        field = getattr(msg, k)
        if hasattr(field, 'CopyFrom'): # composite field
            field.CopyFrom(v)
        else:
            setattr(msg, k, v)
    return msg

# --- qa ---

def request_qa_slots(device):
    """get current footswitch assignments"""
    print('send msg')
    send_message(device, _msg(qASlotsRequest= QASlotsRequest(request=True)))

def set_qa_slots(device, slots):
    """set QA slots to list of preset indexes (length 2)"""
    send_message(device, _msg(qASlotsSet=QASlotsSet(slots=slots)))

# --- firmware ---

def request_firmware_version(device): 
    send_message(device, _msg(firmwareVersionRequest=FirmwareVersionRequest(request=True)))

# --- preset status ---

def request_current_preset(device):
    send_message(device, _msg(currentPresetRequest=CurrentPresetRequest(request=True)))

def set_preset(device, preset_index):
    send_message(device, _msg(loadPreset=LoadPreset(presetIndex=preset_index)))

# --- auditioning ---

def audition_preset(device, preset_json):
    """send a preset JSON string to be temporaily loaded"""
    send_message(device, _msg(auditionPreset=AuditionPreset(presetData=preset_json)))

def request_audition_state(device):
    send_message(device, _msg(auditionStateRequest=AuditionStateRequest(request=True)))

def exit_audition(device):
    send_message(device, _msg(exitAuditionPreset=ExitAuditionPreset(exit=True)))

# --- memory usage ---

def request_memory_usage(device):
    send_message(device, _msg(memoryUsageRequest=MemoryUsageRequest(request=True)))

# --- processor utilization ---

def request_processor_utilization(device):
    send_message(device, _msg(processorUtilizationRequest=ProcessorUtilizationRequest(request=True)))

# --- footswitch mode---

def request_footswitch_mode(device):
    send_message(device, _msg(lt4FootswitchModeRequest=LT4FootswitchModeRequest(request=True)))

# --- usb gain ---

def request_usb_gain(device):
    send_message(device, _msg(usbGainRequest=UsbGainRequest(request=True)))

def set_usb_gain(device, value_db):
    send_message(device, _msg(usbGainSet=UsbGainSet(valueDB=value_db)))

# --- heartbeat ---

def send_heartbeat(device):
    send_message(device, _msg(heartbeat=Heartbeat(dummyField=True)))

# --- sync ---

def send_sync_begin(device):
    send_message(device, _msg(modalStatusMessage=ModalStatusMessage(context=ModalContext.SYNC_BEGIN, state=ModalState.OK)))

def send_sync_end(device):
    send_message(device, _msg(modalStatusMessage=ModalStatusMessage(context=ModalContext.SYNC_END, state=ModalState.OK)))

