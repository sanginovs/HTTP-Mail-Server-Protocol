
'''Author: Sher Sanginov

What is included?
*added checksum to this protocol. The checksum is implemented in the get_message method in both client and server.
Because this is where the message is processed first and then passed into functions. What happens is that every time
a client sends a message to the server or vice verca, the get_message method of the client(or server) will take the message,
separate the checksum from message and then take the rest of the message and compute its checksum. Once it computes, it
compares two checksums. If they are equal, then it returns the message. Otherwise, it sends "Please resend your message" back
to the destination of the corrupted message.
assignment.
*Authentication- the protocol has a way to authenticate different users:
It uses cookies in order to keep track of each user session and requires the clients to register, login and logout.
*The protocol is very user-interactive.
*The Mail Server protocol is multi-threaded. Used threading library to accomplish that.

How to run the code:
In order to run our code, make sure you have Python 2.7 since we implemented the protocol in Python 2.7
Then, go to the terminal and run the server and client files separately. (python server.py localhost 8887)
If you want to run the codes on the IDE like Pycharm, you can comment out sys.argv lines, instead specify
your port and host.


'''

# -*- coding: utf-8 -*-



import base64
import uuid
import threading


# Messaging Server v0.1.0
import socket
import sys


class SimpleMailServerProtocol():
    def __init__(self):
        self.IMQ = []  # incoming_message_queue
        self.MBX = {}  # user_mailboxes
        self.login = {} #registered accounts and passwords
        self.ID = {}  #session ids and usernames
        self.assigned_cookies=[] #to check which session cookies has already been assigned




    def moduli_list_generator(self, string):
        '''checksum generator'''
        count = 0
        for character in string:
            count += ord(character)
        moduli = count % 13
        count=0
        return moduli



    def checksum(self, input_list):
        '''checksum generator'''
        count1=0
        count1 += input_list
        result = count1 % 17
        return result

    def checksum_output(self, string):
        return self.checksum(self.moduli_list_generator(string))


    def send_message_with_checksum(self, message, connection):
        '''sends messages to client by assigning checksum to them'''
        checksum=str(self.checksum_output(message))
        final_message=" ".join([checksum, message])
        connection.send(bytearray(final_message + "\0", encoding="utf-8"))


    # CONTRACT
    # start_server : string number -> socket
    # Takes a hostname and port number, and returns a socket
    # that is ready to listen for requests
    def start_server (self, host, port):

      server_address = (host, port)
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.bind(server_address)
      sock.listen(1)  #listens for connections on specified port
      return sock


      # CONTRACT
      # socket -> boolean
      # Shuts down the socket we're listening on.
    def stop_server(self, sock):
      return sock.close()
    #<------------------------------------------------------------------------------------------------------------>
    def get_message(self, sock):
      chars = []
      connection, client_address = sock.accept()
      print ("Connection from [{0}]".format(client_address))
      try:
          while True:
              char = connection.recv(1)
              if char == bytearray('\0'):
                  break
              if not char:
                  break
              else:
                  # print("Appending {0}".format(char))
                  chars.append(char.decode("utf-8"))
      finally:
          '''checking the checksum of an incoming messages'''
          tuple1= (''.join(chars), connection)
          message=str(tuple1[0])
          crc = int(message.split(" ")[0])
          index=message.find(chr(32))+1
          final_message=message[index:]
          output=self.checksum_output(final_message) #calculate the checksum for the message
          if crc==output:       #compare checksum with the received checksum
              tuple=(final_message, connection)
              return tuple
          else:
              self.send_message_with_checksum("Error, resend the message.", connection)


    def assign_cookie(self, username, conn):
        '''assigns cookie to the a client'''
        if username not in self.ID:  #checking if username doesn't already have a cookie and if cookie is not assigned
            session_id = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
            while session_id in self.assigned_cookies:
                session_id = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
            self.ID[username]=session_id
            self.assigned_cookies.append(session_id)
            cookie= " ".join(["Cookie:", session_id])
            self.send_message_with_checksum(cookie, conn)
            conn.close()
        else:
            if self.ID[username] in self.assigned_cookies:
                self.assigned_cookies.remove(self.ID[username])
            del self.ID[username]
            print username, "has session cookie already"
            self.assign_cookie(username, conn)


    def register(self, message, connection):
          '''Registers a client into the mail server'''
          message=str(message)

          username = message.split(" ")[1]   #splitting username from message
          password= message.split(" ")[2]   #splitting password from message

          if username not in self.login:    #if user is not already registered
              self.login[username]=password #register him/her
              if username not in self.MBX:   #if user does not have a mailbox
                  self.MBX[username]=[]     #create mailbox
              self.send_message_with_checksum("OK. Registered. Please, login now.", connection)
          else:
              self.send_message_with_checksum("KO. You are in our registration list.", connection)
              connection.close()
              return False



    def log_out(self, message, connection):
        message=str(message)
        cookie = message.split(" ")[3]
        username=message.split(" ")[1]
        if username in self.ID:      #if user is already registered
            if self.ID[username]==cookie:
                for i in self.assigned_cookies:
                    if i ==cookie:
                        self.assigned_cookies.remove(i)     #delete user session from assigned session list
                del self.ID[username]
                print "Removed session id of user:", username
                self.send_message_with_checksum("Logged Out.", connection)




    def log_in(self,message,connection):

        message=str(message)
        username = message.split(" ")[1]  # splitting username from message "LOGIN daryl lo 4>
        password = message.split(" ")[2]  # splitting password from message

        if username in self.login:          #if user is registered
            if self.login[username]==password:  #if user account match user password
                print "Success.", username, "is logged in."
                self.assign_cookie(username, connection)    #assign cookie to logged in user
                print "Success. User logged in"

            else:
                self.send_message_with_checksum("Failure. Wrong Password.", connection)
        else:
            print "the client should register first"
            self.send_message_with_checksum("You should register first.", connection)
            connection.close()


    #->adds a client message to IMQ list
    def add_message(self, content, connection):
      content=str(content)
      message1=content.split("|")
      message=message1[1]
      print message
      cookie=message1[2]
      cookie_str=cookie.split(" ")
      cookie2=cookie_str[2]

      if True:
          for i in self.ID:
              if self.ID[i]==cookie2:
                  self.IMQ.append(message)
                  print "message appended"
                  self.send_message_with_checksum("OK. Your message was added.", connection)

      else:
          print "not appended"
          self.send_message_with_checksum("KO! Your message wasn't added.", connection)


    def store(self, message, connection):
        '''stores the most recent message from IMQ list into a client's mailbox'''
        message = str(message)
        cookie = message.split(" ")[3]
        username = message.split(" ")[1]
        if username in self.ID:
            if self.ID[username]==cookie:
                if username in self.MBX:
                    if len(self.IMQ)>0:
                        recent_message = self.IMQ.pop()
                        self.MBX[username].append(recent_message)
                        self.send_message_with_checksum("OK. Your recent message has been stored in user's mailbox.", connection)
                    else:
                        self.send_message_with_checksum("KO. No message in the IMQ.",connection)

            else:
                self.send_message_with_checksum("KO. Your message has not been stored.", connection)


    def count(self, message, connection):
        '''counts user mailbox messages'''
        message = str(message)
        cookie = message.split(" ")[3]
        username = message.split(" ")[1]
        if username in self.ID:
            if self.ID[username]==cookie:
                if username in self.MBX:
                    count = len(self.MBX[username])
                    count=str(count)
                    self.send_message_with_checksum("Your total messages COUNTED:"+count, connection)

                else:
                    self.send_message_with_checksum("KO. Did not count:", connection)


    def delete_message(self, message, connection):
        '''deletes a message from user mailbox'''
        message = str(message)
        cookie = message.split(" ")[3]
        username = message.split(" ")[1]
        if username in self.ID:
            if self.ID[username] == cookie:
                if username in self.MBX:
                    if len(self.MBX[username])>0:
                        self.MBX[username].pop(0)
                        self.send_message_with_checksum("OK. You first message was deleted from MBX.", connection)
                    else:
                        self.send_message_with_checksum("KO. No message on your mailbox.", connection)
                else:
                    self.send_message_with_checksum("KO. was not deleted.", connection)


    def get_client_message(self, message, connection):
        '''pops one message from client mailbox and sends it to a client'''
        message = str(message)
        cookie = message.split(" ")[3]
        username = message.split(" ")[1]
        if username in self.ID:
            if self.ID[username] == cookie:
                if username in self.MBX:
                    if len(self.MBX[username])>0:
                        message = str(self.MBX[username].pop())
                        self.send_message_with_checksum("Your message:" + message, connection)

                    else:
                        self.send_message_with_checksum("KO. No message on your mailbox", connection)

                else:
                    self.send_message_with_checksum("KO. did not get client message", connection)



    def dump(self, msg, conn):
        '''prints all the content of the database in the server for debugging purposes'''
        message = str(msg)
        cookie = message.split(" ")[3]
        username = message.split(" ")[1]
        if username in self.ID:
            if self.ID[username] == cookie:
                print self.MBX
                print self.IMQ
                print self.ID
                print self.assigned_cookies
                print self.login
                self.send_message_with_checksum("OK. Dumped.", conn)

            else:
                print("NO HANDLER FOR CLIENT MESSAGE: [{0}]".format(message))
                self.send_message_with_checksum("KO. No Dump", conn)



# CONTRACT
# handle_message : string socket -> boolean
# Handles the message, and returns True if the server
# should keep handling new messages, or False if the 
# server should shut down the connection andc quit.
    def handle_message (self, msg, conn):
      if msg.startswith("REGISTER"):
        self.register(msg, connection)
      elif msg.startswith("LOGIN"):
        self.log_in(message, conn)
      elif msg.startswith("MESSAGE"):
        self.add_message(msg, conn)
      elif msg.startswith("STORE"):
        self.store(msg, conn)
      elif msg.startswith("COUNT"):
        self.count(msg, conn)
      elif msg.startswith("DELMSG"):
        self.delete_message(msg, conn)
      elif msg.startswith("GETMSG"):
        self.get_client_message(msg, conn)
      elif msg.startswith("LOGOUT"):
        self.log_out(msg, connection)
      elif msg.startswith("DUMP"):
        self.dump(msg, conn)

  
if __name__ == "__main__":
  # Check if the user provided all of the 
  # arguments. The script name counts
  # as one of the elements, so we need at 
  # least three, not fewer.


  if len(sys.argv) < 3:
    print ("Usage: ")
    print (" python server.py <host> <port>")
    print (" e.g. python server.py localhost 8887")
    sys.exit()

  host = sys.argv[1]
  port = int(sys.argv[2])
  #host = "localhost" #or you can put ip of 0.0.0.0 (this ip allows any other ip to connect to this server)
  #port = 8885
  mail_server=SimpleMailServerProtocol()
  sock = mail_server.start_server(host, port)
  print("Running server on host [{0}] and port [{1}]".format(host, port))
  
  RUNNING = True
  while RUNNING:
    message, connection = mail_server.get_message(sock)

    print("MESSAGE: [{0}]".format(message))
    t= threading.Thread(target=mail_server.handle_message, args=(message, connection,)).start()






