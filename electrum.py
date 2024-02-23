import random
import socket
import json

import logging

class Request:
    jsonrpc = "2.0"

    def __init__(self, method: str, params: list):
        self.method = method
        self.params = params
        self.id = random.randint(100000, 999999999)

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

class ElectrumClient:

    def __init__(self, addr="electrum.bitaroo.net", port=50001) -> None:
        self.conn = None
        self.addr = addr
        self.port = port
        self.file = None
        self.subscriptions = {} 

    def connect(self):
        self.conn = socket.create_connection((self.addr, self.port))
        self.file = self.conn.makefile("r")

    def close(self):
        self.conn.close()
    
    def call(self, request: Request) -> dict:
        try:
            self.conn.sendall((request.to_json() + "\n").encode("ascii"))
            return json.loads(self.file.readline()).get("result", {})
        except Exception as error:
            logging.error(str(error), exc_info=True)
            self.close()
            self.connect()
            return self.call(request=request)

    def subscribe(self, method: str, params: list, callback: object = None):
        request = Request(method, params)
        self.subscriptions[request.id] = callback
        self.conn.sendall((request.to_json() + "\n").encode("ascii"))
        return request.id

    def close(self) -> None:
        self.file.close()
        self.conn.close()

    def get_block_header(self, height):
        return self.call(Request("blockchain.block.header", [height]))

    def get_block_headers(self, start_height: int, count: int):
        return self.call(Request("blockchain.block.headers", [start_height, count]))
    
    def get_estimatefee(self, nblocks: int):
        return self.call(Request("blockchain.estimatefee", [nblocks]))

    def get_history(self, address: str):
        return self.call(Request("blockchain.scripthash.get_history", [address]))

    def get_balance(self, address: str):
        return self.call(Request("blockchain.scripthash.get_balance", [address]))

    def listunspent(self, address: str):
        return self.call(Request("blockchain.scripthash.listunspent", [address]))

    def broadcast(self, tx: str):
        return self.call(Request("blockchain.transaction.broadcast", [tx]))

    def subscribe_get_last_block_height(self, callback: object = None):
        return self.subscribe("blockchain.headers.subscribe", [], callback=callback)
    
    def subscribe_scripthash(self, address: str, callback: object = None):
        return self.subscribe("blockchain.scripthash.subscribe", [address], callback=callback)

    def process_subscriptions(self):
        while True:
            r = self.file.readline()
            if not r:
                continue
            else:
                try:
                    r = json.loads(r)
                except:
                    r = dict()
            ...
