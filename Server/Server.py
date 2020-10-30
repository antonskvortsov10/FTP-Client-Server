from socket import *
import sys
import base64

#host = '82.179.143.64'
#'192.168.0.10'
host = '127.0.0.1'
port = 1111 #55554
addr = (host, port)


sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(addr)


# Создание пакета DATA
def createDATA(data, number):
    opcode = '03'
    opcode = bytes(opcode, encoding='utf-8')
    number = '0' + str(number) if number <= 9 else str(number)
    block = bytes(number, encoding='utf-8')
    return opcode + block + data

# Создание пакета ACK
def createACK(number):
    opcode = bytes('04', encoding='utf-8')
    number = '0' + str(number) if number <= 9 else str(number)
    block = bytes(number, encoding='utf-8')
    return opcode + block

# Парсим полученый DATA пакет
def parsingDATA(pack):
    opcode = int(chr(pack[1]))
    print(pack)
    if opcode != 3:
        print('Error: opcode =  %s, expected 3 ' % opcode)
        return []
    numbBlock = int(chr(pack[2]) + chr(pack[3]))
    print('number block: {}'.format(numbBlock))
    i = 4
    return [numbBlock, pack[4:]]


# Принимаем файл
def handlingWRQ(data, clAddr):
    flag = 0
    i = 2
    filename = ''
    while i < len(data):
        if chr(data[i]) != '0':
            filename += chr(data[i])
        else:
            break
        i += 1
    mode = data[i+1:-1].decode() # octet or ...
    if mode != 'octet':
        print('this server supports only mode octet')
    
    sock.sendto(createACK(0), clAddr)

    newFile = open(filename, 'wb')

    packetCounter = 1
    memPack = [0 for i in range(100)]
    while True:
        packet, clAddr = sock.recvfrom(1024)

        data = parsingDATA(packet)
        if data == []:
            return False
        if data[0] > packetCounter:
            packetCounter = data[0]

        memPack[data[0]] = data[1]
        sock.sendto(createACK(data[0]), clAddr)
        
        if len(packet) < 516:
            break

    c = 1
    while c < 100:
        if memPack[c] == 0:
            break
        newFile.write(memPack[c])
        c += 1
    if c >= 100:
        print('blocks > 100 ')
        return False
    if c < packetCounter:
        print('Error: not all packets received')
    newFile.close()


# Отправляем файл
def handlingRRQ(data, clientAddr):
    i = 2
    filename = ''
    while i < len(data):
        if chr(data[i]) != '0':
            filename += chr(data[i])
        else:
            break
        i += 1
    mode = data[i+1:-1].decode() # octet or ...
    if mode != 'octet':
        print('this server supports only mode octet')

    newFile = open(filename, 'rb')

    block = newFile.read(512)
    number = 1
    flag = 0
    while True:
        dataNew = createDATA(block, number)
        number += 1
        sock.sendto(dataNew, clientAddr)
        print('Packet sended')
        ack, addr = sock.recvfrom(1024)
        if flag == 1:
            sock.close()
            break
        if chr(ack[1]) != '4':
            print('Error: packet is not ack')
            return False
        block = newFile.read(512)
        if len(block) < 512:
            flag = 1


if __name__ == '__main__':
    # Ожидание пакета WRQ/RRQ
    data, clientAddr = sock.recvfrom(1024)
    print('Connected: {} {}'.format(clientAddr[0], clientAddr[1]))
    print(data)
    
    opcode = int(chr(data[0]) + chr(data[1]))
    
    if opcode == 2:
        handlingWRQ(data, clientAddr)
    if opcode == 1:
        handlingRRQ(data, clientAddr)
    
    sock.close()
