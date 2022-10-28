import spade_rpc
import aioxmpp

import asyncio
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

import getpass

def get_dataset(file):
    file = open(file, 'r')

    dataset = [x.split(',') for x in file][:-1]
    x = np.double([x[0:3] for x in dataset])
    y = np.asarray([x[4][:-2] for x in dataset])
    
    x = x.tolist()
    y = y.tolist()

    return x, y

class NeighborsClassifier(spade_rpc.rpc.RPCAgent):
    def fit(self, x, y):
        self.classifier.fit(x, y)

    async def setup(self):
        def predict(x):
            print('Predicting')
            prediction = self.classifier.predict([x])
            print('Sending prediction')
            return prediction.tolist()

        self.classifier = KNeighborsClassifier(n_neighbors=3)
        self.rpc.register_method(predict, 'predict')

class Client(spade_rpc.rpc.RPCAgent):
    async def ask_to(self, JID, x):
        if type(JID) == list:
            return [self.ask_to(jidx, x) for jidx in JID]

        return await self.rpc.call_method(aioxmpp.JID.fromstr(JID), 'predict', x)

async def main(jid, passwd):
    x, y = get_dataset('iris.data')
    
    c1 = NeighborsClassifier("{}/c1".format(jid), passwd)
    future = c1.start()
    future.result()

    print('training c1')
    c1.fit(x, y)
    print('c1 trained')

    client = Client("{}/client".format(jid), passwd)
    future = client.start()
    future.result()
    
    print('asking {}'.format([x[0]]))
    result = await client.ask_to("{}/c1".format(jid), [x[0]])
    print(result)

if __name__ == "__main__":
    jid = input("JID> ")
    passwd = getpass.getpass()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main(jid, passwd))
    finally:
        loop.close()    