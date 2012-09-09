from construct import *
from utils import pack

pkt_type = Enum(Byte('pkt_type'),
                command = 1,
                async_data = 2,
                sync_data = 3,
                event = 4,
                )

cmd_opcode = Enum(ULInt16('cmd_opcode'),
                  rx_test = 0x201d,
                  tx_test = 0x201e,
                  test_end = 0x201f,
                  util_reset = 0xfe80,
                  )

event_opcode = Enum(Byte('event_opcode'),
                    cmd_complete = 0x0e,
                    )


event_status = Enum(Byte('event_status'),
                    success = 0x00,
                    disallowed = 0x0c,
                    )

test_pattern = Enum(Byte('test_pattern'),
                    psn9 = 0,
                    z1100 = 1,
                    z1010 = 2,
                    psn15 = 3,
                    z1111 = 4,
                    z0000 = 5,
                    z0011 = 6,
                    z0101 = 7,
                    )

param_len = OneOf(Byte("param_len"), range(0, 256))
channel = OneOf(Byte("channel"), range(0,40))

event_status_struct = Struct("event_status",
                             event_status,
                             )
							
test_end = Struct("test_end",
                  Embed(event_status_struct),
                  ULInt16("pkt_count"),
                  )	

rx_test_cmd_struct = Struct("rx_test",
                        channel,
                        )

tx_test_cmd_struct = Struct("tx_test",
                        channel,
                        OneOf(Byte("payload_len"), range(0,38)),
                        test_pattern,
                        )

cmd_complete_struct = Struct("cmd_complete",
                                 Byte("flow_control"),
                                 cmd_opcode,
                                 Switch("cmd_response", lambda ctx: ctx["cmd_opcode"],
                                        {
                                            "rx_test": event_status_struct,
                                            "tx_test": event_status_struct,
                                            "test_end": test_end,
                                            }
                                        )
                                 )

hci_event = Struct("hci_event",
                   event_opcode,
                   param_len,
                   Switch("event_params", lambda ctx: ctx["event_opcode"],
                          {
                              "cmd_complete":	cmd_complete_struct,
                              }
                          )
                   )

hci_cmd = Struct("hci_cmd",
                 cmd_opcode,
                 param_len,
                 Switch("cmd_params", lambda ctx: ctx["cmd_opcode"],
                        {
                            "rx_test": rx_test_cmd_struct,
                            "tx_test": tx_test_cmd_struct,
                            },
                        default = MetaRepeater(lambda ctx: ctx["param_len"], Byte("cmd_params")),
                        )
                 )
						

hci_pkt = Struct("hci_pkt",
                 pkt_type,
                 Switch("pkt_type", lambda ctx: ctx["pkt_type"],
                        {
                            "command": Embed(hci_cmd),
                            "event": Embed(hci_event),
                            }
                        )
                 )

def build(input):
    return hci_pkt.build(input)

def parse(input):
    return hci_pkt.parse(input)
    