from spade.behaviour import OneShotBehaviour
import spade_rpc
import aioxmpp

import classifiers as clfs
from sklearn.utils._testing import ignore_warnings
from sklearn.exceptions import ConvergenceWarning

import numpy as np
import time
import getpass


def get_dataset(file, shuffle=True, test_split=0.1):
    file = open(file, 'r')

    dataset = [x.split(',') for x in file][:-1]
    x = np.double([x[0:3] for x in dataset])
    y = np.asarray([x[4][:-1] for x in dataset])

    if shuffle:
        p = np.random.permutation(len(x))
        x, y = x[p], y[p]


    train_len = int(len(x) - len(x)*test_split)
    x_train = x[:train_len]
    x_test = x[train_len:]

    y_train = y[:train_len]
    y_test = y[train_len:]

    return (x_train.tolist(), y_train.tolist()), (x_test.tolist(), y_test.tolist())

class Client(spade_rpc.rpc.RPCAgent):
    async def ask_to(self, JID, x):
        if type(JID) == list:
            return [await self.ask_to(jidx, x) for jidx in JID]

        return await self.rpc.call_method(aioxmpp.JID.fromstr(JID), 'predict', x)

class AskBehaviour(OneShotBehaviour):
    def __init__(self, classifiers_jids, x):
        super().__init__()
        self.classifiers_jids = classifiers_jids
        self.x = x

    async def run(self):
        predictions = await self.agent.ask_to(self.classifiers_jids, self.x)
        predictions = np.array(predictions)
        for i in range(len(predictions)):
            results = predictions[:,i]

            values, counts = np.unique(results, return_counts=True)
            ind = np.argmax(counts)

            print('Most common prediction for {}: {}'.format(self.x[0][i], values[ind]))

        await self.agent.stop()

def main(jid, passwd):
    (x_train, y_train), (x_test, y_test) = get_dataset('iris.data')
    
    classifiers = clfs.register_classifiers(jid, passwd, clfs.classifiers, [x_train, y_train])

    client = Client("{}/client".format(jid), passwd)

    ab = AskBehaviour(list(classifiers), [x_test])
    ab.set_agent(client)
    client.add_behaviour(ab)

    future = client.start()
    future.result()

    while client.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            client.stop()            
            break

if __name__ == "__main__":
    np.random.seed(722)

    jid = input("JID> ")
    passwd = getpass.getpass()

    main(jid, passwd)