import struct
import socket
import json
import time

def unpack_varint(s):
    d = 0
    for i in range(5):
        n = s.recv(1)
        print(n)
        if len(n) != 0:
            b = ord(n)
            d |= (b & 0x7F) << 7*i
            if not b & 0x80:
                break
    return d

def pack_varint(d):
    o = b""
    while True:
        b = d & 0x7F
        d >>= 7
        o += struct.pack("B", b | (0x80 if d > 0 else 0))
        if d == 0:
            break
    return o

def pack_data(d):
    return pack_varint(len(d)) + d

def pack_port(i):
    return struct.pack('>H', i)

def get_info(host='localhost', port=25565):
    '''
        get minecraft je server info
    '''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
    except Exception as error:
        return {'error':error}
    # Send handshake + status request
    s.send(pack_data(b"\x00\x00" + pack_data(host.encode('utf8')) + pack_port(port) + b"\x01"))
    s.send(pack_data(b"\x00"))

    # Read response
    unpack_varint(s)     # Packet length
    unpack_varint(s)     # Packet ID
    l = unpack_varint(s) # String length

    d = b""
    while len(d) < l:
        d += s.recv(1024)

    # Close our socket
    s.close()

    # Load json and return
    return json.loads(d.decode('utf8'))


def mcpe_info_dict(host='localhost', port=19132):
    '''
        get minecraft be server info
    '''
    try:
        t1 = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr = (host,port)
        s.sendto(b'\x01\x00\x00\x00\x00$\r\x12\xd3\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x124Vx\n', addr)
        response, addr = s.recvfrom(1024)
        t2 = time.time()
        n = 0
        for i in response:
            n += 1
            if i == 59:
                break
        data = response[n:].decode().split(';')
        if len(data) >= 1:
            if data[1] == '':
                return {'status':'offline','error':''}
        else:
            return {'status':'offline','error':''}
        return  {'status':'online','ip':host,'port':port,'motd':data[0],'agreement':data[1],'version':data[2],'online':data[3],'max':data[4],'gamemode':data[7],'delay':int(round(t2 - t1, 3) * 1000)}
    except Exception as e:
        return {'status':'offline','error':str(e)}

