import serial
import time
import os
import sys

# YMODEM协议常量
SOH = b'\x01'  # 128字节数据包开始
STX = b'\x02'  # 1024字节数据包开始
EOT = b'\x04'  # 传输结束
ACK = b'\x06'  # 确认
NAK = b'\x15'  # 否定确认
CAN = b'\x18'  # 取消传输
CRC = b'C'  # CRC模式


class YModemSender:
    def __init__(self, serial_port):
        self.serial = serial_port

    def calculate_crc(self, data):
        crc = 0
        for byte in data:
            crc = crc ^ (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc = crc << 1
            crc = crc & 0xFFFF
        return crc

    def wait_for_char(self, expected_char, timeout=10):
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            if self.serial.in_waiting:
                char = self.serial.read()
                if char == expected_char:
                    return True
        return False

    def send_packet(self, packet_num, data):
        # 准备数据包
        packet = SOH
        packet += bytes([packet_num])
        packet += bytes([255 - packet_num])

        # 确保数据长度为128字节
        data = data.ljust(128, b'\x1A')
        packet += data

        # 添加CRC
        crc = self.calculate_crc(data)
        packet += bytes([crc >> 8])
        packet += bytes([crc & 0xFF])

        # 发送数据包
        for _ in range(10):  # 最多重试10次
            self.serial.write(packet)
            if self.wait_for_char(ACK, 1):
                return True
        return False

    def send_file(self, filename):
        try:
            # 等待接收方发送'C'
            if not self.wait_for_char(CRC, 10):
                print("未收到接收方的CRC请求")
                return False

            # 发送文件名数据包
            file_size = os.path.getsize(filename)
            file_info = f"{os.path.basename(filename)}\x00{str(file_size)}\x00".encode()
            if not self.send_packet(0, file_info):
                print("发送文件信息失败")
                return False

            # 打开并发送文件内容
            with open(filename, 'rb') as file:
                packet_num = 1
                while True:
                    data = file.read(128)
                    if not data:
                        break

                    print(f"\r发送数据包 {packet_num}", end='')
                    if not self.send_packet(packet_num, data):
                        print("\n发送数据包失败")
                        return False
                    packet_num = (packet_num + 1) % 256

            # 发送EOT
            print("\n发送第一个EOT")
            self.serial.write(EOT)
            if not self.wait_for_char(ACK, 1):
                print("第一个EOT未被确认")
                return False

            print("发送第二个EOT")
            self.serial.write(EOT)
            if not self.wait_for_char(ACK, 1):
                print("第二个EOT未被确认")
                return False

            print("\n文件传输完成")
            return True

        except Exception as e:
            print(f"传输错误: {str(e)}")
            return False


def main():
    # 配置串口
    # 注意：COM口需要根据实际情况修改
    port = "COM12"  # Windows示例
    baudrate = 115200

    try:
        # 打开串口
        ser = serial.Serial(port, baudrate, timeout=1)
        sender = YModemSender(ser)

        # 发送文件
        # 注意：文件路径需要根据实际情况修改
        filename = "../../STM32F103rb_App1.bin"
        if sender.send_file(filename):
            print("文件传输成功！")
        else:
            print("文件传输失败！")

        # 关闭串口
        ser.close()

    except Exception as e:
        print(f"错误: {str(e)}")


if __name__ == "__main__":
    main()