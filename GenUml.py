import os
import json
import requests
import zopfli
import urllib.parse
import argparse

class BeautifulJson():
    def __init__(self, file_path: str, offline_port="8080") -> None:
        with open(file_path, "r", encoding="utf-8") as f:
            json_file = json.load(f)
        json_str = json.dumps(json_file)
        self.s = "@startjson\n" + json_str + "\n@endjson"

        self.OnlineUrl = "https://www.plantuml.com/plantuml"
        self.OfflineUrl = f"http://127.0.0.1:{offline_port}"

    def Genb64Str(self):
        compressor = zopfli.ZopfliDeflater()
        data = compressor.compress(self.s.encode()) + compressor.flush()
        # print(data)
        data_b64 = self.encode64_(data)
        # print(d2)
        return data_b64
    
    def GenUrlOnline(self, b64str: str, format: str = "svg"):
        return f"{self.OnlineUrl}/{format}/{b64str}" 

    def GenUrlOffline(self, b64str: str, format: str = "svg"):
        return f"{self.OfflineUrl}/{format}/{b64str}"
    
    def GenPng(self, url: str, outputname: str):
        response = requests.get(url)
        with open("temp.svg", "wb") as f:
            f.write(response.content)
        os.system(f"inkscape -z --export-png={output_filename} -d 300 temp.svg")
        os.remove("temp.svg")

    def encode64_(self, e):
        r = ""
        for i in range(0, len(e), 3):
            if i + 2 == len(e):
                r += self.append3bytes(e[i], e[i + 1], 0)
            elif i + 1 == len(e):
                r += self.append3bytes(e[i], 0, 0)
            else:
                r += self.append3bytes(e[i], e[i + 1], e[i + 2])
        return r

    def append3bytes(self, e, n, t):
        c1 = e >> 2
        c2 = ((3 & e) << 4) | (n >> 4)
        c3 = ((15 & n) << 2) | (t >> 6)
        c4 = 63 & t
        r = ""
        r += self.encode6bit(63 & c1)
        r += self.encode6bit(63 & c2)
        r += self.encode6bit(63 & c3)
        r += self.encode6bit(63 & c4)
        return r

    def encode6bit(self, e):
        if e < 10:
            return chr(48 + e)
        elif e < 36:
            return chr(65 + e - 10)
        elif e < 62:
            return chr(97 + e - 36)
        elif e == 62:
            return "-"
        else:
            return "_"

    def encodeURIComponent(self, s):
        return urllib.parse.quote(s, safe='~()*!.\'')

    def unescape(self, s):
        s = s.replace("+", " ")
        return urllib.parse.unquote(s)

    def unescape_encodeURIComponent(self, s):
        return self.unescape(self.encodeURIComponent(s))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='BeautifulJson command line tool')
    parser.add_argument('filename', help='the input file')
    args = parser.parse_args()

    # json_filename = "streams/streams.json"
    json_filename = args.filename

    output_filename = json_filename.split('.')[-2] + ".png"
    solution = BeautifulJson(json_filename)
    # print(solution.s)
    b64str = solution.Genb64Str()
    url = solution.GenUrlOnline(b64str) # 使用官方的在线服务器
    # url = solution.GenUrlOffline(b64str) # 使用本地docker部署的服务器
    print(url)
    solution.GenPng(url, output_filename)

    print(f"{output_filename} generated.")
    print("Done.")