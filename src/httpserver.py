import subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import os
from time import sleep
import json

id_dict = {}
id_max = {}


def run_calculations(id):
    print('calculations: ' + id)
    id_dict[id] = -1
    sleep(5)
    with open('resources/' + id + '/res.png', 'wb') as res:
        with open('resources/' + id + '/im1.png', 'rb') as image:
            res.write(image.read())
    id_dict[id] = -2
    print('end of calculations: ' + id)


class MyHandler(SimpleHTTPRequestHandler):
    res_path = './resources/'

    def do_POST(self):
        length = self.headers['content-length']
        type = self.headers['content-type']
        if type == 'image/png':
            id = os.path.dirname(self.path)[1:]
            if id in id_dict:
                if id_dict[id] >= 0:
                    data = self.rfile.read(int(length))
                    with open(self.res_path + self.path, 'wb') as f:
                        f.write(data)
                    id_dict[id] += 1
                    print('add file: ' + self.path)
                if id_dict[id] == id_max[id]:
                    run_calculations(id)
        if type == 'application/json':
            data = self.rfile.read(int(length))
            if not os.path.exists(self.res_path + self.path):
                with open(self.res_path + self.path, 'wb') as f:
                    f.write(data)
                with open(self.res_path + self.path) as f:
                    data = json.load(f)
                    id = data['id']
                    num = data['count']
                    if not os.path.exists(id):
                        os.mkdir(self.res_path + id)
                    if id not in id_dict:
                        id_dict[id] = 0
                        id_max[id] = int(num)
                os.remove(self.res_path + self.path)
                print('add: ' + id)
        self.send_response(200)

    def do_GET(self):
        f = self.send_head()
        id = os.path.dirname(self.path)[11:]
        print(id)
        if id in id_dict and id_dict[id] == -2:
            if f:
                try:
                    self.copyfile(f, self.wfile)
                    print('copyfile')
                finally:
                    f.close()
                    id_dict.pop(id)
                    subprocess.call('rm -rf ' + self.res_path + id, shell=True)
            self.send_response(200)
            return
        self.send_response(404)


if __name__ == '__main__':
    server = ThreadingHTTPServer(('localhost', 8000), MyHandler)
    server.serve_forever()
