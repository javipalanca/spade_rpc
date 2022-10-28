import spade_rpc

class AgentClassifier(spade_rpc.rpc.RPCAgent):
    def __init__(self, jid, passwd):
        super().__init__(jid, passwd)

    async def setup(self):
        def predict(x):
            prediction = self.classifier.predict(x)
            return prediction.tolist()

        self.rpc.register_method(predict, 'predict')

def register_classifiers(jid, passwd, classifiers, training_data):
    method_classifiers = classifiers.copy()

    [classifier.fit(*training_data) for classifier in method_classifiers]
    
    classifiers_jids = []
    for classifier in method_classifiers:
        classifier_name = type(classifier).__name__
        classifier_jid = '{}/{}'.format(jid, classifier_name)

        agent_classifier = AgentClassifier(classifier_jid, passwd)
        future = agent_classifier.start()
        future.result()

        agent_classifier.classifier = classifier
        classifiers_jids.append(classifier_jid)

    return classifiers_jids

import sklearn
import sklearn.neighbors 
import sklearn.neural_network 
import sklearn.svm

classifiers = [
    sklearn.neighbors.KNeighborsClassifier(),
    sklearn.neural_network.MLPClassifier(),
    sklearn.svm.SVC(),
    sklearn.svm.LinearSVC(),
]