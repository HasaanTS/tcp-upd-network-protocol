# SYED HASSAAN TAUQEER
# BSCS-3A

#SERVER PIPELINED


from BadNet5 import*
import sys
from socket import *
import time

#addr
ip = "localhost"
port = int(sys.argv[1]) #55000
j_port = 50505
ack_mssg = "ack"
sock = socket(AF_INET,SOCK_DGRAM)
addr = (ip,port)

#controllers
exp_ack = 0
ack_num = -1 # current -- UPDATE this for all intents 
ack_ed = -1 # previous
wndw_it = 0 #go to 4 and reset

file_buff = [] # put the file here
#--------------------------------------------------CHECK SUM----------------------------

# Code taken from http://codewiki.wikispaces.com/ip_checksum.py.


def ip_checksum(data):  # Form the standard IP-suite checksum
    pos = len(data)
    if (pos & 1):  # If odd...
        pos -= 1
        sum = ord(data[pos])  # Prime the sum with the odd end byte
    else:
        sum = 0

    #Main code: loop to calculate the checksum
    while pos > 0:
        pos -= 2
        sum += (ord(data[pos + 1]) << 8) + ord(data[pos])

    sum = (sum >> 16) + (sum & 0xffff)
    sum += (sum >> 16)

    result = (~ sum) & 0xffff  # Keep lower 16 bits
    result = result >> 8 | ((result & 0xff) << 8)  # Swap bytes
    return chr(result / 256) + chr(result % 256)

#--------------------------------------------------------------------------------------
sock.bind(addr)#listener

print "Ready to serve"




file_size = sock.recv(1024)
print "file size"
print file_size

list_size = sock.recv(1024)
list_size = int(list_size)
print "list size:", list_size



file_buff = [""]*list_size 
# initialized the file with empty strings------------------------


file_name = "d_Intro.pdf"


f_handle = open(file_name, 'wb')

rcvd_size = 0
prev_data = ""

start = time.time()

while rcvd_size <= file_size :
 
	if (rcvd_size > file_size):
		break

	incoming,server = sock.recvfrom(1024)
	wndw_it += 1
	
	incomingData = incoming.split(" , ")	
	ack_num = int(incomingData[0]) #extract ack
	rcvdChk = str(incomingData[1]) #extract chksum
	data = str(incomingData[2])
	temp_pack = str(ack_num) + " , " + str(0) + " , " + str(data)

	cal = ip_checksum(temp_pack)
		
	if ( (ack_num > exp_ack) and (cal == rcvdChk) and (file_buff[ack_num] == "") ): # OUT OF ORDER
		file_buff.insert(ack_num, data)#put data in appropriate position
		rcvd_size += len(data)#file write the packet
		prev_data = data
		if ("EOF" in data):
			print "EOF!"
			break
		
		print "{0:.2f}".format((rcvd_size/float(file_size))*100)+ "% Done"
		print '==========='


	if ( (ack_num == exp_ack) and (cal == rcvdChk) and (file_buff[ack_num] == "") ): #NEW PACK
			
		exp_ack = ack_num + 1
		ack_ed = ack_num

		if(data == prev_data):
			print "repeat"
			#if(data == ""): # last end when file is complete
			#	break
		else:
			rcvd_size += len(data)#file write the packet
			file_buff.insert(ack_num, data)#put data in appropriate position
			prev_data = data
		if ("EOF" in data):
			print "EOF!"
			break
		
		print "{0:.2f}".format((rcvd_size/float(file_size))*100)+ "% Done"
		print '==========='
			


	if (wndw_it == 4): #window size done
		wndw_it = 0			
		chk = 0
		ack = str(ack_ed) + " , " + str(chk) + " , " + ack_mssg
		chk = ip_checksum(ack)
		ack = str(ack_ed) + " , " + str(chk) + " , " + ack_mssg
		BadNet.transmit(sock, ack, ip, 50505)	
			

i = 0
while i != ( len(file_buff)-1 ) : # writing to file
	f_handle.write(file_buff[i])
	i += 1


finish = time.time()

taken = finish - start
	
print "downloaded"
print "took :" + str(taken) + "seconds"
	
