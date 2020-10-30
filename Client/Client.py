import socket
import sys
import base64


def createWRQorRRQ(fileN, opcode):
    if (opcode != 1 or opcode != 2):
        print('Error: not a valid opcode for WRQ or RRQ')
    opcode = bytes('0' + str(opcode), encoding='utf-8')
    filename = bytes(fileN, encoding='utf-8')
    mode = bytes('octet', encoding='utf-8')
    zero = bytes('0', encoding='utf-8')
    return opcode + filename + zero + mode + zero

def createDATA(number, data):
    opcode = '03'
    opcode = bytes(opcode, encoding='utf-8')
    number = '0' + str(number) if number <= 9 else str(number)
    block = bytes(number, encoding='utf-8')
    if type(data) == type("any string"):
        data = bytes(data, encoding='utf-8')
    return opcode + block + data

def createACK(number):
    opcode = '04'
    opcode = bytes(opcode, encoding='utf-8')
    number = '0' + str(number) if number <= 9 else str(number)
    block = bytes(number, encoding='utf-8')
    return opcode + block

def createERROR(errorCode, errMsg):
    opcode = '05'
    opcode = bytes(opcode, encoding='utf-8')
    errorCode = '0' + str(errorCode) if errorCode <= 9 else str(errorCode)
    errorCode = bytes(errorCode, encoding='utf-8')
    zero = bytes('0', encoding='utf-8')
    return opcode + errorCode + errMsg + zero



def Client1(Fname):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = ('127.0.0.1', 1111)
    RRQ = createWRQorRRQ(Fname, 1)
    sock.sendto(RRQ, addr)
    num = 1
    f = True    
    while True:
        print(num)
        data, addr1 = sock.recvfrom(516)
        if f:
            if data[:2] == '05':
                print('ERROR: code error: ' + data[2:4])
                sock.close()
                return 0
            snum = str('0' + str(num)) if len(str(num)) < 2 else str(num)
            if str(data[2:4])[2:4] == snum:
                ACK = createACK(num)
                sock.sendto(ACK, addr)
                file = open(Fname, 'wb')
                file.write(data[4:])
                num += 1
            else:
                print('Error in num ' + str(num))
                sock.settimeout(0.5)
                continue
            f = False
        else:
            if data[:2] == '05':
                print('ERROR: code error: ' + data[2:4])
                sock.close()
                file.close()
                return 0
            snum = str('0' + str(num)) if len(str(num)) < 2 else str(num)
            if str(data[2:4])[2:4] == snum:
                ACK = createACK(num)
                sock.sendto(ACK, addr)
                num += 1
                file.write(data[4:])
                if len(data) < 516:
                    break
            else:
                print('Error in num ' + str(num))
                sock.settimeout(0.5)
                continue
    sock.close()
    file.close()
    print('Считывание файла выполнилось успешно')
    return 1

def Client2(Fname):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = ('127.0.0.1', 1111)
    WRQ = createWRQorRRQ(Fname, 2)
    print(WRQ)
    sock.sendto(WRQ, addr)
    f = True
    stop = False
    num = 1
    while True:
        print(num)
        pack, addr1 = sock.recvfrom(516)
        if f:
            if pack[:2] == '05':
                print('ERROR: code error: ' + data[2:4])
                print('sock close')
                sock.close()
                return 0
            snum = str('0' + str(num)) if len(str(num)) < 2 else str(num)
            if str(pack[2:4])[2:4] == '00':
                file = open(Fname, 'rb')
                s = file.read(512)
                data = createDATA(num, s)
                if len(s) < 512:
                    sock.sendto(data, addr)
                    break
                sock.sendto(data, addr)
            else:
                print('Error in num ' + str(num - 1))
                sock.settimeout(0.5)
                continue
            f = False
        else:
            if pack[:2] == '05':
                print('ERROR: code error: ' + data[2:4])
                sock.close()
                file.close()   
                return 0
            snum = str('0' + str(num)) if len(str(num)) < 2 else str(num)
            if str(pack[2:4])[2:4] == snum:
                s = file.read(512)
                num += 1
                data = createDATA(num, s)
                if len(s) < 512:
                    sock.sendto(data, addr)
                    break
                sock.sendto(data, addr)
            else:
                print('Error in num ' + str(num))
                sock.settimeout(0.5)
                continue
    f = True
    while f:
        pack, addr1 = sock.recvfrom(516)
        snum = str('0' + str(num)) if len(str(num)) < 2 else str(num)
        if str(pack[2:4])[2:4] == snum:
            f = False
        else:
            print('Что-то осталось')
            sock.sendto(data, addr)
    sock.close()
    file.close()
    print('Отправление файла выполнилось успешно')
    return 1


if __name__ == '__main__':
    '''
    Client1("myimage.jpg")  # на сервере лежит файл, считываем его
    Client2("myimage.jpg")  # на клиенте лежит файл, отправляем его на сервер
    '''
            



