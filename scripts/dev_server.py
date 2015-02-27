__author__ = 'Blake'

import SimpleHTTPServer
import SocketServer

port = 8000

handler = SimpleHTTPServer.SimpleHTTPRequestHandler
httpd = SocketServer.TCPServer(('', port), handler)

if __name__ == '__main__':
    print 'Serving on port %d' % port
    httpd.serve_forever()