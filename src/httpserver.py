import subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import os
from time import sleep
import json

from reconstruction import runReconstruction

id_dict = {}
id_max = {}


def run_calculations(id):
    print('calculations: ' + id)
    id_dict[id] = -1
    # start of your code
    # files in folder = 'resources/' + id with original names, result must be located in this folder too
    runReconstruction('../resources/' + id)

    # sleep(5)
    # with open('resources/' + id + '/images/res.png', 'wb') as res:
    #     with open('resources/' + id + '/images/im1.png', 'rb') as image:
    #         res.write(image.read())
    # end of your code
    id_dict[id] = -2
    print('end of calculations: ' + id)


class MyHandler(SimpleHTTPRequestHandler):
    res_path = './resources'

    def do_POST(self):
        length = self.headers['content-length']
        type = self.headers['content-type']
        print('type = ' + type)
        if type == 'image/png':
            id = os.path.dirname(self.path)[1:].replace('/images', '')
            print('id in POST = ' + id)

            if id in id_dict:
                if id_dict[id] >= 0:
                    data = self.rfile.read(int(length))
                    with open(self.res_path + self.path, 'wb') as f:
                        f.write(data)
                    id_dict[id] += 1
                    print('add file: ' + self.path)
                print('id_dict[id] = ' + str(id_dict[id]) + ' id_max[id] = ' + str(id_max[id]))
                if id_dict[id] == id_max[id]:
                    run_calculations(id)
        if type == 'application/json':
            data = self.rfile.read(int(length))
            print('self.res_path + self.path : ' + self.res_path + self.path)
            if not os.path.exists(self.res_path + self.path):
                with open(self.res_path + self.path, 'wb') as f:
                    f.write(data)
                with open(self.res_path + self.path) as f:
                    data = json.load(f)
                    id = data['id']
                    num = data['count']
                    if not os.path.exists(id):
                        os.mkdir(self.res_path + '/' + id)
                        os.mkdir(self.res_path + '/' + id + '/images')
                    if id not in id_dict:
                        id_dict[id] = 0
                        id_max[id] = int(num)
                os.remove(self.res_path + self.path)
                print('add: ' + id)
        self.send_response(200)

    def do_GET(self):
        print('self.path = ' + self.path)
        f = self.send_head()
        id = os.path.dirname(self.path)[1:].replace('resources/', '').replace('/images', '').replace('/reconstruction_sequential/PMVS/models', '')
        print('id = ' + id)
        if id in id_dict and id_dict[id] == -2:
            if f:
                try:
                    self.copyfile(f, self.wfile)
                finally:
                    f.close()
                    id_dict.pop(id)
                    # subprocess.call('rm -rf ' + self.res_path + '/' + id, shell=True)
            self.send_response(200)
            return
        self.send_response(404)


if __name__ == '__main__':
    server = ThreadingHTTPServer(('localhost', 8000), MyHandler)
    server.serve_forever()