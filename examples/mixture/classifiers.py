import spade_rpc
import sklearn
import sklearn.neighbors 
import sklearn.neural_network 
import sklearn.svm

class NeighborsClassifier(spade_rpc.rpc.RPCAgent):
    def __init__(self, jid, passwd, training_data):
        super().__init__(jid, passwd)
        self.classifier = sklearn.neighbors.KNeighborsClassifier()
        self.classifier.fit(*training_data)

    async def setup(self):
        def predict(x):
            prediction = self.classifier.predict(x)
            return prediction.tolist()

        self.rpc.register_method(predict, 'predict')

class MLPClassifier(spade_rpc.rpc.RPCAgent):
    def __init__(self, jid, passwd, training_data):
        super().__init__(jid, passwd)
        self.classifier = sklearn.neural_network.MLPClassifier()
        self.classifier.fit(*training_data)
    
    async def setup(self):
        def predict(x):
            prediction = self.classifier.predict(x)
            return prediction.tolist()

        self.rpc.register_method(predict, 'predict')

class SVCClassifier(spade_rpc.rpc.RPCAgent):
    def __init__(self, jid, passwd, training_data):
        super().__init__(jid, passwd)
        self.classifier = sklearn.svm.SVC()
        self.classifier.fit(*training_data)
    
    async def setup(self):
        def predict(x):
            prediction = self.classifier.predict(x)
            return prediction.tolist()

        self.rpc.register_method(predict, 'predict')

class LinearSVCClassifier(spade_rpc.rpc.RPCAgent):
    def __init__(self, jid, passwd, training_data):
        super().__init__(jid, passwd)
        self.classifier = sklearn.svm.LinearSVC()
        self.classifier.fit(*training_data)
    
    async def setup(self):
        def predict(x):
            prediction = self.classifier.predict(x)
            return prediction.tolist()

        self.rpc.register_method(predict, 'predict')