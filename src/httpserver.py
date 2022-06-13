from pathlib import PurePath
import subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler, HTTPServer
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
    data_dir = os.path.abspath('resources/' + id)
    runReconstruction(data_dir)
    os.chdir('../../..')

    # sleep(5)
    # os.mkdir('resources/' + id + '/reconstruction_sequential')
    # os.mkdir('resources/' + id + '/reconstruction_sequential/PMVS')
    # os.mkdir('resources/' + id + '/reconstruction_sequential/PMVS/models')
    # with open('resources/' + id + '/reconstruction_sequential/PMVS/models/pmvs_options.txt.ply', 'wb') as res:
    #     with open('resources/b96a34a8-1014-44cc-a8b3-75378eb1dacf/reconstruction_sequential/PMVS/models/pmvs_options.txt.ply', 'rb') as image:
    #         res.write(image.read())
    # sleep(240)
    # with open('resources/' + id + '/res.png', 'wb') as res:
    #     with open('resources/' + id + '/images/im1.png', 'rb') as image:
    #         res.write(image.read())
    # end of your code
    id_dict[id] = -2
    print('end of calculations: ' + id)


class MyHandler(SimpleHTTPRequestHandler):
    res_path = os.path.abspath('/resources')

    def do_POST(self):
        res_path = os.path.abspath('resources')
        length = self.headers['content-length']
        type = self.headers['content-type']
        print('type = ' + type)
        if type == 'image/png':
            id = os.path.dirname(self.path)[1:].replace('/images', '')
            print('id in POST = ' + id)

            if id in id_dict:
                if id_dict[id] >= 0:
                    # print('rfile ' + self.rfile.name)
                    data = self.rfile.read(int(length))
                    with open(res_path + self.path, 'wb') as f:
                        f.write(data)
                    id_dict[id] += 1
                    print('add file: ' + self.path)
                print('id_dict[id] = ' + str(id_dict[id]) + ' id_max[id] = ' + str(id_max[id]))
                if id_dict[id] == id_max[id]:
                    run_calculations(id)
        if type == 'application/json; charset=utf-8':
            # res_path = os.path.abspath('resources')
            # print('res_path = ' + res_path) 
            data = self.rfile.read(int(length))
            print('self.res_path + self.path : ' + res_path + self.path)
            if not os.path.exists(res_path + self.path):
                with open(res_path + self.path, 'wb') as f:
                    f.write(data)
                with open(res_path + self.path) as f:
                    data = json.load(f)
                    id = data['id']
                    num = data['count']
                    if not os.path.exists(id):
                        os.mkdir(res_path + '/' + id)
                        os.mkdir(res_path + '/' + id + '/images')
                    if id not in id_dict:
                        id_dict[id] = 0
                        id_max[id] = int(num)
                os.remove(res_path + self.path)
                print('add: ' + id)
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        print('self.path in GET = ' + self.path)
        # str = self.path[1:]
        # self.path = os.path.abspath(str)
        # print('self.path in GET = ' + self.path)
        # print('translated' + self.translate_path(self.path))
        f = self.send_head()
        id = os.path.dirname(self.path).replace('/resources/', '').replace('/reconstruction_sequential/PMVS/models', '')
        print('id in GET = ' + id)

        if id in id_dict and id_dict[id] == -2:
            if f:
                try:
                    self.copyfile(f, self.wfile)
                finally:
                    f.close()
                    id_dict.pop(id)
                    subprocess.call('rm -rf ./resources/' + id, shell=True)
            self.send_response(200)
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()


if __name__ == '__main__':
    server = ThreadingHTTPServer(('localhost', 8000), MyHandler)
    server.serve_forever()
