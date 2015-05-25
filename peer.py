import thread               # for running client and server simultaneously
import socket               # Import socket module
from socket import *
import datetime
import time
import os
from Tkinter import *       # for gui
from random import randint
import sys

tracker_ip=''
firstroot=Tk()
Label(firstroot, text="Enter Tracker IP").grid(row=0,column=0,pady=4,padx=4)
gettrackerip=Entry(firstroot)
gettrackerip.pack()
gettrackerip.grid(row=1,column=0,pady=4,padx=4)

def connect():
    global tracker_ip
    tracker_ip=str(gettrackerip.get())
    
    firstroot.destroy()

Button(firstroot, text='Connect', command=(lambda : connect())).grid(row=2, column=0, sticky=W, pady=4,padx=4)

print tracker_ip
firstroot.mainloop()

root = Tk()
getfilename=Entry(root)
#getfilename.pack()
getfilename.grid(row=1,column=2,pady=4,padx=4)
Label(root, text="PeerList").grid(row=0,column=0,pady=4,padx=4)
getfilename.insert(0,"file.ext")

listbox=Listbox(root)
listbox.grid(row=1,column=0,pady=4,padx=4)
mybox=Listbox(root)
mybox.grid(row=3,column=0,pady=4,padx=4,)
Label(root, text="MyFiles").grid(row=2,column=0,pady=4,padx=4)
varstr=StringVar()
varstr.set("started")
lab=Label(root,textvariable=varstr)
lab.grid(row=6,column=4)

filebox=Listbox(root)
filebox.grid(row=3,column=2,pady=4,padx=4)
Label(root, text="Filelist").grid(row=2,column=2,pady=4,padx=4)
downloadstat=StringVar()
downloadstat.set("")
Label(root, textvariable=downloadstat).grid(row=5,column=3,pady=4,padx=4)
print "creating sharedfolder"
try:
    os.makedirs("sharedfolder")
except WindowsError,e:
    print "folder already exists"
    
def tracker():
        #import socket
    peerlist=dict()
    peerlistold=dict()
    while True:
        
        t = socket(AF_INET,SOCK_STREAM)         # Create a socket object
        host = tracker_ip #socket.gethostname() # Get local machine name
        port = 55555                # Reserve a port for your service.
        try:
            t.connect((host, port))
            t.send("refresh")
            received = t.recv(1024)
            #print "in client"
            print received
            t.send(str(os.listdir("sharedfolder")))
            t.shutdown(1)
            t.close()
            peer_list=eval(received)
            listbox.delete(0, END)
            for item in peer_list:
                listbox.insert(END, item)
            #listbox.pack()
            
            mybox.delete(0, END)
            x=os.listdir("sharedfolder")
            for item in x:
                mybox.insert(END, item)
            #mybox.pack()
            
            
            flag =0
            peerlist=dict(peerlistold)
            peerlistold=dict(peer_list)
            for item in peerlist.items():
                for items in peer_list.items():
                    if item[0]==items[0]:
                        del peerlist[item[0]]
                        del peer_list[items[0]]
            if not peer_list:
                yy=1
            else:
                print str(peer_list)+'joined'
                varstr.set(str(peer_list.keys())+'joined')
                #lab.pack()
            if not peerlist:
                yy=1
            else:
                print str(list(peerlist))+'left'
                varstr.set(str(peerlist.keys())+'left')
                #lab.pack()
                
                
        except:
            #print "error from tracker" +str(err)
            print "error from tracker"
            t.close()
        
        time.sleep(1)
        varstr.set('')
        #label.pack()
def download_file():
        #global downloadstat
        #downloadstat=StringVar()
        #downloadstat.set("")
        #listbox=Listbox(root)
        #for item in [randint(0,9),randint(0,9),randint(0,9)]:
        #    listbox.insert(END, item)
        #listbox.pack()
        #listbox.grid(row=0,column=0)
        s = socket(AF_INET,SOCK_STREAM)         # Create a socket object
        host = tracker_ip #socket.gethostname() # Get local machine name
        port = 55555                # Reserve a port for your service.
        s.connect((host, port))
        try:    
            s.send("download")
            sendfilename = getfilename.get()
            time.sleep(0.1)
            s.send(str(sendfilename))
            iplist=s.recv(1024)
            print iplist
            iplist=eval(iplist)
            for x in iplist:
                print x
                if str(x)==str(gethostbyname(gethostname())):
                    print "already you have the file"
                    del iplist[iplist.index(x)]
            print iplist
            if not iplist:
                print 'file not found'
               
                downloadstat.set("file not found")
                s.close()
            else:
                print str(len(iplist))+ 'peers found'
                randomgen = randint(0,len(iplist)-1)
                downloadstat.set(str(len(iplist))+ 'peers found - Downloading from' +str(iplist[randomgen]))
                
                s.close()
                thread.start_new_thread(peer_connect,(iplist[randomgen],sendfilename))
        except:
            print "error from download file"
            s.close()
        print "in client"
                            # Close the socket when done

def peer_connect(ipaddr,sendfilename):
    n = socket(AF_INET,SOCK_STREAM)                                    
    host = str(ipaddr)
    port =12345
    tim=datetime.datetime.now()
    try:
        n.connect((host, port))
        n.send(str(sendfilename))
        f = open("sharedfolder/"+str(sendfilename),'wb')
        try:
            l = n.recv(1024)
            while (l):
                print 'Receiving...'
                f.write(l)
                l = n.recv(1024)
            f.close()
            print "Done Receiving"
        except:
            print "error in file reception"
            f.close()
                        
        print n.recv(1024)
        n.send("file received")
        #a.destroy()
        #b=Label(root, text='Downloaded').grid(row=5,column=3,pady=4,padx=4)
        #b.destroy()
        n.shutdown(1)
        timeinsec=(datetime.datetime.now()-tim).total_seconds()
        filesize=long(os.stat("sharedfolder/"+str(sendfilename)).st_size)
        print timeinsec
        if timeinsec < 1:
            timeinsec=(datetime.datetime.now()-tim).microseconds
            filesize=filesize*1000000
            print filesize
        
        throughput = float(filesize)/long(timeinsec)
        downloadstat.set(str(throughput)+ 'bytes/second' + '  ' + str(timeinsec)+ 'seconds'+ '   ' + str(filesize))
               
    except:
        #print "error in connection from peer connect"+str(err)
        print "error in connection from peer connect"
    
    #n.shutdown(socket.SHUT_WR)
    n.close()
    

def request_file():
    s_req = socket(AF_INET,SOCK_STREAM)
    host = tracker_ip
    print tracker_ip
    port = 55555                # Reserve a port for your service.
    s_req.connect((host, port))
    try:    
        s_req.send("filelist")
        filelist=s_req.recv(4096)
        filelist=eval(filelist)
        print filelist
        
        for x in filelist.items():
            print str(x[0])
            print str(gethostbyname(gethostname()))
            if str(x[0])==str(gethostbyname(gethostname())):
                print "inside if"
                del filelist[x[0]]
        print filelist        
        filebox.delete(0, END)
        for item in filelist.items():
            for items in item[1]:
                filebox.insert(END, items)
        #filebox.pack()
        
    except:
        print "error in connection from req file"
    s_req.close


        
def client():    
    root.title("PEER TO PEER")
    root.geometry("800x800")
    Button(root, text='Search And Download', command=(lambda : download_file())).grid(row=1, column=1,  pady=4,padx=4)
    Button(root, text='Request file list', command=(lambda : request_file())).grid(row=2, column=1,  pady=4,padx=4)
    Button(root, text='close', command=(lambda : close_window())).grid(row=5, column=1, pady=4,padx=4)
    root.mainloop()
    

def server():
    global b
    b = socket(AF_INET,SOCK_STREAM)         # Create a socket object
    host = gethostname() # Get local machine name
    port = 12345                # Reserve a port for your service.
    b.bind((host, port))        # Bind to the port
    print "server"
    b.listen(5)                 # Now wait for client connection.
    while True:
       c, addr = b.accept()     # Establish connection with client.
       print 'Got connection from', addr
       try:
           receivefilename = c.recv(1024)
           f_s=open("sharedfolder/"+receivefilename,'rb')
           k=f_s.read(1024)
           try:
               while (k):        
                   print 'Sending...'
                   c.send(k)
                   k = f_s.read(1024)
               f_s.close()
               print "Done Sending"
               c.shutdown(1)
           except:
                print "error in transmission"
                f_s.close()
           #c.shutdown(socket.SHUT_WR)
           print c.recv(1024)
       except:
           print "connection lost from server"
           
       c.close()                # Close the connection

def close_window():
    b.close
    root.destroy()
    exit()
#def set_ip():
#    tracker_ip=str(gettrackerip.get())
#    popup.destroy()

#popup = Tk()
#gettrackerip=Entry(popup)
#gettrackerip.pack()
#gettrackerip.grid(row=0,column=0)
#Button(popup, text='enter ip', command=(lambda : set_ip())).grid(row=1, column=1, sticky=W, pady=4)
#popup.mainloop()
#print tracker_ip
thread.start_new_thread(server,())
thread.start_new_thread(tracker,())
thread.start_new_thread(client,())

