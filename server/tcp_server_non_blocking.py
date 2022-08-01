import socket
import select
import queue
from server import tcp_server
import json

class TCPServerNonBlocking(tcp_server.TCPServer):
    ''' A Non-blocking multi-client TCP Server '''

    def __init__(self, host, port, viz):
        super().__init__(host, port)
        self.input_list = []        # read sockets
        self.output_list = []       # write sockets
        self.client_requests = {}   # client request queues
        self.viz = viz

    def configure_server(self):
        ''' Configure the server'''

        # create a TCP / IPv4 socket
        self.printwt('Creating socket...')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.printwt('Socket created')

        # make the socket non-blocking
        self.sock.setblocking(0)

        # bind server to the address
        self.printwt(f'Binding server to {self.host}:{self.port}...')
        self.sock.bind((self.host, self.port))
        self.printwt(f'Server binded to {self.host}:{self.port}')

        # append the input list to include this new socket
        self.input_list.append(self.sock)

    def accept_connection(self):
        '''Accept connection from a client'''

        # accept client's connection request
        print("yo 1")
        client_sock, client_address = self.sock.accept()
        self.printwt(f'Accepted connection from {client_address}')

        # make the client socket non-blocking
        client_sock.setblocking(0)
        print("yo 2")
        # put this client socket in the input list
        self.input_list.append(client_sock)
        print("yo 3")
        # create a request queue for the client
        self.client_requests[client_sock] = (client_address, queue.Queue())

    def close_client_socket(self, client_sock):
        '''Close client socket after the client has closed its connection'''

        client_address = self.client_requests[client_sock][0]

        # remove client from the output list
        if client_sock in self.output_list:
            self.output_list.remove(client_sock)

        # remove it from the input list as well
        self.input_list.remove(client_sock)

        # remove client's request queue
        del self.client_requests[client_sock]

        # close the client socket
        client_sock.close()

        self.printwt(f'Closed client socket for {client_address}')

    def receive_message(self, client_sock):
        ''' Receive client's request and put it on the client's request queue '''

        try:
            # receive request from the client
            data_enc = client_sock.recv(1024)

            if not data_enc:
                # empty request denotes connection closed by client
                # so we'll close the client socket
                self.close_client_socket(client_sock)

            else:
                # otherwise acknowledge the client's request
                raw = data_enc.decode('utf-8')
                fin = "".join([raw.rsplit("}" , 1)[0] , "}"])
                print(data_enc, raw, len(raw))
                data = json.loads(fin)
                client_address = self.client_requests[client_sock][0]
                self.printwt(f'[ REQUEST from {client_address} ]')
                print('\n', data, '\n')
                self.viz.args.update(truncate_psi=data["truncate_psi"])

                # save request in the client's request queue
                self.client_requests[client_sock][1].put(data)

                # put the client on the output list
                if client_sock not in self.output_list:
                    self.output_list.append(client_sock)

        # handle any forced / unexpected closing of connection by the client
        except OSError as err:
            self.printwt(err)
            self.close_client_socket(client_sock)

    def handle_client(self, client_sock):
        ''' Send response to the client '''

        try:
            # take out request from client's request queue
            # name = self.client_requests[client_sock][1].get_nowait()
            # print("HANDLE_CLIENT", name)
            resp = "ty"
            # send response to the client
            client_address = self.client_requests[client_sock][0]
            # self.printwt(f'[ RESPONSE to {client_address} ]')
            # client_sock.sendall(resp.encode('utf-8'))
            # print('\n', resp, '\n')

        # this handles a condition where client socket is in the writable list
        # even though it's been removed from the dictionary.
        except KeyError as err:
            pass

        # when client has no active requests
        except queue.Empty:
            self.output_list.remove(client_sock)

        # handle any other connection error that might occur
        except OSError as err:
            self.printwt(err)
            self.close_client_socket(client_sock)

    def handle_exception(self, client_sock):
        ''' Close the socket where exception was caught '''

        self.printwt('Closing error socket...')
        self.close_client_socket(client_sock)
        self.printwt('Error socket closed')

    def wait_for_client(self):
        ''' Listen for incoming connections and handle them '''

        # queue upto max 10 connection requests
        self.sock.listen(10)

        try:
            while True: # keep alive
            # while not self.viz.should_close(): # keep alive
                # select would return three lists (rlist, wlist, xlist)
                # rlist contains sockets that have something to be read from
                # wlist contains sockets that must be written to
                # xlist contains sockets that generated exceptional conditions
                readable_socks, writable_socks, error_socks = select.select(self.input_list,
                self.output_list, self.input_list)
                # read from readable sockets
                for sock in readable_socks:
                    # if the socket is server socket, accept the connection
                    if sock is self.sock:
                        self.accept_connection()
                    # otherwise receive the client request
                    else:
                        self.receive_message(sock)

                # send response to writable sockets
                for sock in writable_socks:
                    self.handle_client(sock)

                # handle exceptional sockets
                for sock in error_socks:
                    self.handle_execption(sock)
                
                self.viz.draw_frame()

          # shutdown the server when user presses Ctrl-C
        except KeyboardInterrupt:
            self.shutdown_server()
            self.viz.close()

    def shutdown_server(self):
        ''' Shutdown the server '''

        self.printwt('Shutting down server...')
        del self.output_list            # remove output list
        del self.client_requests        # remove request queues
        for sock in self.input_list:    # close active client sockets
            sock.close()
        del self.input_list             # remove input list
        self.sock.close()               # close server socket