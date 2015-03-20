"""
Based on Abhishek Thakur's BTB script
"""

import pandas as pd
import scipy as sp
import numpy as np
from sklearn.cluster import KMeans
from sklearn.cross_validation import train_test_split
from sklearn import ensemble, feature_extraction, preprocessing

# multiclass loss
def MultiLogLoss(y_true, y_pred, eps = 1e-15):
    """Multi class version of Logarithmic Loss metric.
    https://www.kaggle.com/wiki/MultiClassLogLoss

    idea from this post:
    http://www.kaggle.com/c/emc-data-science/forums/t/2149/is-anyone-noticing-difference-betwen-validation-and-leaderboard-error/12209#post12209

    Parameters
    ----------
    y_true : array, shape = [n_samples]
    y_pred : array, shape = [n_samples, n_classes]

    Returns
    -------
    loss : float
    """
    predictions = np.clip(y_pred, eps, 1 - eps)

    # normalize row sums to 1
    predictions /= predictions.sum(axis=1)[:, np.newaxis]

    actual = np.zeros(y_pred.shape)
    rows = actual.shape[0]
    actual[np.arange(rows), y_true.astype(int)] = 1
    vsota = np.sum(actual * np.log(predictions))
    return -1.0 / rows * vsota
    
label_binary = preprocessing.LabelBinarizer()

# import data
train = pd.read_csv('Data/train.csv')
test = pd.read_csv('Data/test.csv')
sample = pd.read_csv('Data/sampleSubmission.csv')

# drop ids and get labels
labels = train.target.values
train = train.drop('id', axis=1)
train = train.drop('target', axis=1)
test = test.drop('id', axis=1)

# transform counts to TFIDF features
tfidf = feature_extraction.text.TfidfTransformer()
train = tfidf.fit_transform(train).toarray()
test = tfidf.transform(test).toarray()

# generate and add clustering features
kmean = KMeans(n_clusters = 6, verbose = 1)
clusters6 = kmean.fit_transform(train)
clusters6_test = kmean.transform(test)
clusters6 /= np.amax(clusters6)

kmean = KMeans(n_clusters = 9, verbose = 1)
clusters9 = kmean.fit_transform(train)
clusters9_test = kmean.transform(test)
clusters9 /= np.amax(clusters9)

kmean = KMeans(n_clusters = 12, verbose = 1)
clusters12 = kmean.fit_transform(train)
clusters12_test = kmean.transform(test)
clusters12 /= np.amax(clusters12)

train = np.hstack((train, clusters6, clusters9, clusters12))
test = np.hstack((test, clusters6_test, clusters9_test, clusters12_test))

# encode labels 
lbl_enc = preprocessing.LabelEncoder()
labels = lbl_enc.fit_transform(labels)


# set up datasets for cross eval
#x_train, x_test, y_train, y_test = train_test_split(train, labels)
#label_binary.fit(y_test)

# train a random forest classifier
clf = ensemble.GradientBoostingClassifier(n_estimators = 1000, verbose = 1)
clf.fit(train, labels)

# predict on test set
#preds_cv = clf.predict_proba(x_test)
preds = clf.predict_proba(test)

# ----------------------  create submission file  -----------------------------
preds = pd.DataFrame(preds, index = sample.id.values, columns = sample.columns[1:])
preds.to_csv('Preds/boostedtrees_kmeansfeats.csv', index_label = 'id')

# ----------------------  cross eval  -----------------------------------------

#y_test = label_binary.inverse_transform(y_test)
#y_test = LabelEncoder().fit_transform(y_test)

#print 'Multiclass Log Loss:', MultiLogLoss(y_test, preds)