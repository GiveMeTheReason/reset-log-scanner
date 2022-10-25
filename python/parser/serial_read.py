import serial


class Ring:
    def __init__(self, port: str = 'COM3', baud: int = 115200, timeout: float = 0.1):
        self._serial = serial.Serial(port, baud, timeout=timeout)
        self._buf = bytearray(b'')
        self._msg = bytearray(b'')
        self._range_datatype_len = 2
        self._clock_datatype_len = 4

        self.measurements = [[]]

    def close(self):
        self._serial.close()

    def process(self):
        self.measurements = [[]]
        self._buf += self._serial.read(self._serial.in_waiting)

        while len(self._buf) >= 3:
            if self._buf[0] == 0xFF and self._buf[1] == 0xFF:
                # btarr[0] and btarr[1] is 0xFF starting bytes
                packet_length = self._buf[2] + 2
                if len(self._buf) >= packet_length:
                    if len(self.measurements[0]) == 0:
                        msg_num = 0
                        total_len = len(self._buf)

                    self._msg = self._buf[0:packet_length]
                    self._buf = self._buf[packet_length:]
                    sensors_num = self._msg[3]
                    data_length = self._range_datatype_len * sensors_num

                    if data_length > packet_length:
                        # print("Too long message! Skip measurement.")
                        self._buf = self._buf[data_length:]
                    else:
                        crc = 0
                        for i in range(2, data_length + self._clock_datatype_len + 3):
                            crc = (crc + self._msg[i]) & 0xFF
                        crc = ~(crc & 0xFF) & 0xFF

                        if (crc == (self._msg[-1] & 0xFF)):
                            if (len(self.measurements[0]) == 0):
                                self.measurements = [[0]*(sensors_num + 1) for _ in range(total_len // packet_length)]

                            ranges = [0.] * sensors_num

                            for i in range(sensors_num):
                                for j in range(self._range_datatype_len):
                                    ranges[i] += float(self._msg[4+2*i+j] << 8*j)

                            clock = 0.0
                            for i in range(self._clock_datatype_len):
                                clock += float(self._msg[4+data_length+i] << 8*i)

                            for i in range(sensors_num):
                                self.measurements[msg_num][i] = ranges[i]

                            self.measurements[msg_num][-1] = clock
                            msg_num += 1
                            # print("fine message: " + f'Packet length {packet_length}, sensors_num {sensors_num}, ranges = {ranges[0]}, {ranges[1]}; clock_ms = {clock}')

                        else:
                            # print("Corrupted message! Skip measurement.")
                            self._buf = self._buf[(data_length + self._clock_datatype_len + 3):]
                else:
                   return self.measurements

            else:
                self._buf = self._buf[1:]
        return self.measurements
