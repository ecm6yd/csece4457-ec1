#!/usr/bin/env python3

import socket
import sys
import select

from file_reader import FileReader


class Jewel:

    def __init__(self, port, file_path, file_reader):
        self.file_path = file_path
        self.file_reader = file_reader

        cookies = b''
        content_type = b''
        status_code = b''
        file_size = b''
        body = b''
        file_contents = b''
        response = ''
        server = 'ecm6yd'

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', port))

        s.listen(5)

        read_from = [s]
        write_to = []

        while True:
            readable, writable, exceptional = select.select(read_from, write_to, read_from)

            for i in readable:
                if i is s:
                    (client, address) = i.accept()
                    print("[CONN] Connection from" + str(address) + " on port " + str(port))
                    readable.append(client)
                else:
                    data = i.recv(1024)
                    if not data:
                        break

                    header_end = data.find(b'\r\n\r\n')
                    if header_end > -1:
                        header_string = data[:header_end]
                        lines = header_string.split(b'\r\n')

                        request_fields = lines[0].split()
                        headers = lines[1:]

                        for header in headers:
                            header_fields = header.split(b':')
                            key = header_fields[0].strip()
                            val = header_fields[1].strip()
                            if key == "Cookie":
                                cookies = val

                        print("[REQU] [" + str(address) + ":" + str(port) + "] " + request_fields[
                            0].decode() + " request for " + request_fields[1].decode())

                        # SET RESPONSE CODE
                        if request_fields[0] == b'GET':
                            file_contents = file_reader.get(file_path + request_fields[1].decode(), cookies)
                            file_size = file_reader.head(file_path + request_fields[1].decode(), cookies)
                            status_code = '200 OK'
                            if file_contents is None and file_size is None:
                                status_code = '404 Not Found'
                                print("[ERRO] [" + str(address) + ":" + str(port) + "] " + request_fields[
                                    0].decode() + " request returned error 404")
                        elif request_fields[0] == b'HEAD':
                            file_size = file_reader.head(file_path + request_fields[1].decode(), cookies)
                            status_code = '200 OK'
                            if file_size is None:
                                status_code = '404 Not Found'
                                print("[ERRO] [" + str(address) + ":" + str(port) + "] " + request_fields[
                                    0].decode() + " request returned error 404")
                        else:
                            status_code = '501 Method Unimplemented'
                            print("[ERRO] [" + str(address) + ":" + str(port) + "] " + request_fields[
                                0].decode() + " request returned error 501")

                        # SET CONTENT TYPE
                        if request_fields[1].find(b'.') > 0:
                            if request_fields[1].decode()[request_fields[1].find(b'.') + 1:] == "css":
                                content_type = 'text/css'
                            elif request_fields[1].decode()[request_fields[1].find(b'.') + 1:] == "html":
                                content_type = 'text/html'
                            elif request_fields[1].decode()[request_fields[1].find(b'.') + 1:] == "txt":
                                content_type = 'text/txt'
                            elif request_fields[1].decode()[request_fields[1].find(b'.') + 1:] == "png":
                                content_type = 'image/png'
                            elif request_fields[1].decode()[request_fields[1].find(b'.') + 1:] == "jpeg":
                                content_type = 'image/jpeg'
                            elif request_fields[1].decode()[request_fields[1].find(b'.') + 1:] == "jpg":
                                content_type = 'image/jpg'
                            elif request_fields[1].decode()[request_fields[1].find(b'.') + 1:] == "gif":
                                content_type = 'image/gif'
                        elif request_fields[1].find(b'.') < 0:
                            content_type = 'text/html'
                            body = '<html><body><h1>' + request_fields[1].decode() + '</h1></body></html>'

                        # SET RESPONSE
                        if status_code == '404 Not Found':
                            response = 'HTTP/1.1 ' + status_code + '\r\n\r\n'
                        elif status_code == '501 Method Unimplemented':
                            response = 'HTTP/1.1 ' + status_code + '\r\n\r\n'
                        elif status_code == '200 OK' and request_fields[0].decode() == "GET" and content_type == 'text/html':
                            response = ('HTTP/1.1 ' + status_code + '\r\n' +
                                        'Content-Type: ' + content_type + '\r\n' +
                                        'Content-Length: ' + str(file_size) + '\r\n' +
                                        'Server: ' + server + '\r\n\r\n' +
                                        body)
                        elif status_code == '200 OK' and request_fields[0].decode() == "GET":
                            response = ('HTTP/1.1 ' + status_code + '\r\n' +
                                        'Content-Type: ' + content_type + '\r\n' +
                                        'Content-Length: ' + str(file_size) + '\r\n' +
                                        'Server: ' + server + '\r\n\r\n' +
                                        file_contents.decode())
                        elif status_code == '200 OK' and request_fields[0].decode() == "HEAD":
                            response = ('HTTP/1.1 ' + status_code + '\r\n' +
                                        'Content-Type: ' + content_type + '\r\n' +
                                        'Content-Length: ' + str(file_size) + '\r\n' +
                                        'Server: ' + server + '\r\n\r\n')

                    i.send(response.encode())
                    readable.remove(i)
                    i.close()


if __name__ == "__main__":
    port = int(sys.argv[1])
    file_path = sys.argv[2]

    FR = FileReader()

    J = Jewel(port, file_path, FR)
