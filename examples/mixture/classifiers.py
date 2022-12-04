import spade_rpc
import random

class AgentClassifier(spade_rpc.rpc.RPCAgent):
    def __init__(self, jid, passwd):
        super().__init__(jid, passwd)

    async def setup(self):
        def predict(*x):
            prediction = self.classifier.predict(x)
            return prediction.tolist()

        self.rpc.register_method(predict, 'predict')

def register_classifier(jid, passwd, classifier, training_data):
    classifier.fit(*training_data)
    classifier_name = type(classifier).__name__
    classifier_jid = '{}/{}{}'.format(jid, classifier_name, random.randint(0,1000))

    agent_classifier = AgentClassifier(classifier_jid, passwd)
    future = agent_classifier.start()
    future.result()

    agent_classifier.classifier = classifier

    return classifier_jid

def register_classifiers(jid, passwd, classifiers, training_data):
    method_classifiers = classifiers.copy()

    classifiers_jids = [register_classifier(jid, passwd, x, training_data) for x in method_classifiers]

    return classifiers_jids

import sklearn
import sklearn.neighbors 
import sklearn.neural_network 
import sklearn.svm
import sklearn.ensemble
import sklearn.naive_bayes
import sklearn.discriminant_analysis
import sklearn.gaussian_process

'''
classifiers = [
    #sklearn.neighbors.KNeighborsClassifier(),
    sklearn.neural_network.MLPClassifier(),
    sklearn.svm.SVC(),
    sklearn.svm.LinearSVC(),
    sklearn.gaussian_process.GaussianProcessClassifier(),
    sklearn.ensemble.RandomForestClassifier(),
    sklearn.tree.DecisionTreeClassifier(),
    sklearn.ensemble.AdaBoostClassifier(),
    sklearn.naive_bayes.GaussianNB(),
    #sklearn.discriminant_analysis.QuadraticDiscriminantAnalysis()
]
'''

classifiers = [
    sklearn.svm.LinearSVC(),
    sklearn.svm.LinearSVC(),
    sklearn.svm.LinearSVC(),
    sklearn.svm.LinearSVC(),
    sklearn.svm.LinearSVC()
]