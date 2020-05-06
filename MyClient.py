# SYED HASSAAN TAUQEER
# BSCS-3A

#CLIENT PIPELINED


from BadNet5 import*
import os
import sys
from socket import *
import time

#addresses
ip = "localhost"
port = int(sys.argv[1]) #55000
j_port = 50505

reader = 1000 # data size
file_buff = [] # store entire file

#window and movers
wndw_l = 0
wndw_r = 3
wndw_it = 0

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

sock = socket(AF_INET,SOCK_DGRAM)
r_sock = socket(AF_INET,SOCK_DGRAM)
r_sock.bind((ip,j_port))#listener

file_name = sys.argv[2] #"Intro.pdf"
f_size = str(os.path.getsize(file_name))


f = open(file_name, 'rb') 


seq_no = 0 # limit it to 10,00,000 for len 8 byte addition. Read 1000 bytes of data from file

chunk = f.read(reader)
chk = 0
pckt = str(seq_no) + " , " + str(chk) + " , " + chunk
chk = ip_checksum(pckt)
pckt = str(seq_no) + " , " + str(chk) + " , " + chunk

file_buff.append(pckt)
print "reading..."

while chunk != "":
	chunk = f.read(reader)
	seq_no += 1
	chk = 0
	pckt = str(seq_no) + " , " + str(chk) + " , " + chunk
	chk = ip_checksum(pckt)
	pckt = str(seq_no) + " , " + str(chk) + " , " + chunk
	file_buff.append(pckt)
print "sending..."
#file read and stored in file_buff

print "file size:"
print f_size
BadNet.transmit(sock, f_size, ip, port) # send file size.


list_size = len(file_buff)
BadNet.transmit(sock, str(list_size), ip, port) # sending number of elements of the list
print "list size:", list_size

start = time.time()
while wndw_it <= (len(file_buff)-1):# try except timeout for every sent
	
	

	while (wndw_it <= wndw_r):
		if(wndw_it == list_size+1):
			break
		pckt = file_buff[wndw_it]
		BadNet.transmit(sock, pckt, ip, port) # after transport reduce window
		wndw_it += 1
	
	if (wndw_it == list_size):
		break

	r_sock.settimeout(0.05)
	try :
		ans,serv = r_sock.recvfrom(1024)# highest successful ack send higher packets	
		
		ansData = ans.split(" , ") # ack0 + chk1 + mssg2
		succ_ack = int(ansData[0])
		rcvdChk = str(ansData[1])
		mssg = str(ansData[2])

		temp_pack = str(succ_ack) + " , " + str(0) + " , " + str(mssg)
		cal = ip_checksum(temp_pack)

		if ( (cal == rcvdChk) and (wndw_it < list_size) ):

			if ( (succ_ack > wndw_l) and (succ_ack < wndw_r) ):#between
				wndw_l = succ_ack + 1
				wndw_r = wndw_l + 3
				wndw_it  = wndw_l

			if (succ_ack == wndw_r):#complete
				wndw_l = wndw_r + 1
				wndw_r = wndw_l + 3
				wndw_it  = wndw_l

			if (succ_ack == wndw_l):#one move
				wndw_l += 1
				wndw_r = wndw_l + 3		
				wndw_it  = wndw_l

	except timeout:

		wndw_it = wndw_l

finish = time.time()
taken = finish - start


print "Uploaded!"

print " taken : %s seconds" % taken
