# -*- coding: utf-8 -*-
"""anis1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1B2GlDNQuQirap9EpdbJcoM20Gy7uh3eV
"""



from google.colab import drive
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
import numpy as np 
import pandas as pd 
import re
import nltk 
import matplotlib.pyplot as plt
# %matplotlib inline

airline_tweets = pd.read_csv('/content/drive/MyDrive/Tweets.csv')
airline_tweets.head()

airline_tweets.airline.value_counts().plot(kind='pie', autopct='%1.2f%%')

airline_tweets.airline_sentiment.value_counts().plot(kind='pie', autopct='%1.0f%%', colors=["#ad5e5e", "#6b8e96", "green"])

airline_sentiment = airline_tweets.groupby(['airline', 'airline_sentiment']).airline_sentiment.count().unstack()
airline_sentiment.plot(kind='bar')

import seaborn as sns

sns.barplot(x='airline_sentiment', y='airline_sentiment_confidence' , data=airline_tweets,palette='hls')

from nltk.corpus import stopwords

from wordcloud import WordCloud, STOPWORDS

nltk.download('stopwords')

def remove_mentions(input_text):
    '''
    Function to remove mentions, preceded by @, in a Pandas Series
    '''
    return re.sub(r'@\w+', '', input_text)

def remove_stopwords(input_text):
    '''
    Function to remove English stopwords from a Pandas Series.
    '''
    stopwords_list = stopwords.words('english')
    # Some words which might indicate a certain sentiment are kept via a whitelist
    whitelist = ["n't", "not", "no"]
    words = input_text.split() 
    clean_words = [word for word in words if (word not in stopwords_list or word in whitelist) and len(word) > 1] 
    return " ".join(clean_words)

df = pd.read_csv('/content/drive/MyDrive/Tweets.csv')
df = df.reindex(np.random.permutation(df.index))  
df = df[['text', 'airline_sentiment']]
df.text = df.text.apply(remove_stopwords).apply(remove_mentions)

positive_df = df[df['airline_sentiment'] == 'positive']
negative_df = df[df['airline_sentiment'] == 'negative']
neutral_df = df[df['airline_sentiment'] == 'neutral']

positive_text = ' '.join(positive_df['text'].tolist())
positive_wordcloud = WordCloud(width=800, height=800, background_color='white').generate(positive_text)
plt.figure(figsize=(7, 8), facecolor=None)
plt.imshow(positive_wordcloud)
plt.axis("off")
plt.tight_layout(pad=0)
plt.show()

negative_text = ' '.join(negative_df['text'].tolist())
negative_wordcloud = WordCloud(width=800, height=800, background_color='white').generate(negative_text)
plt.figure(figsize=(8, 8), facecolor=None)
plt.imshow(negative_wordcloud)
plt.axis("off")
plt.tight_layout(pad=0)
plt.show()

neutral_text = ' '.join(neutral_df['text'].tolist())
neutral_wordcloud = WordCloud(width=800, height=800, background_color='white').generate(neutral_text)
plt.figure(figsize=(8, 8), facecolor=None)
plt.imshow(neutral_wordcloud)
plt.axis("off")
plt.tight_layout(pad=0)
plt.show()

df.head()

df.shape

# Count number of each type of tweet
df['airline_sentiment'].value_counts()

from sklearn.model_selection import train_test_split

# Splitting the dataset
X_train, X_test, y_train, y_test = train_test_split(df.text, df.airline_sentiment, test_size=0.1, random_state=37)

print('# Train data samples:', X_train.shape[0])
print('# Test data samples:', X_test.shape[0])
assert X_train.shape[0] == y_train.shape[0]
assert X_test.shape[0] == y_test.shape[0]

import collections
import keras
from keras.preprocessing.text import Tokenizer
from keras.utils.np_utils import to_categorical

NB_WORDS = 10000  # Parameter indicating the number of words we'll put in the dictionary

MAX_LEN = 30  # Maximum number of words in a sequence

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report

from keras.preprocessing.text import Tokenizer

tk = Tokenizer(num_words=NB_WORDS,
               filters='!"#$%&()*+,-./:;<=>?@[\]^`{|}~\t\n',
               lower=True,
               char_level=False,
               split=' ')
tk.fit_on_texts(X_train)

print('Fitted tokenizer on {} documents'.format(tk.document_count))
print('{} words in dictionary'.format(tk.num_words))
print('Top 5 most common words are:', collections.Counter(tk.word_counts).most_common(5))

X_train_oh = tk.texts_to_matrix(X_train, mode='count')
X_test_oh = tk.texts_to_matrix(X_test, mode='count')

from sklearn.preprocessing import LabelEncoder

# Create a label encoder object and fit on the training labels
le = LabelEncoder()
le.fit(y_train)

# Convert the training and test labels to numerical form
y_train_le = le.transform(y_train)
y_test_le = le.transform(y_test)

# Get the list of classes from the label encoder object
classes = list(le.classes_)

# Convert the numerical labels to one-hot encoded form
from keras.utils import to_categorical
y_train_oh = to_categorical(y_train_le, num_classes=len(classes))
y_test_oh = to_categorical(y_test_le, num_classes=len(classes))

X_train_rest, X_valid, y_train_rest, y_valid = train_test_split(X_train_oh, y_train_oh, test_size=0.1, random_state=37)

assert X_valid.shape[0] == y_valid.shape[0]
assert X_train_rest.shape[0] == y_train_rest.shape[0]

print('Shape of validation set:', X_valid.shape)

from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.optimizers import Adam

BATCH_SIZE = 512
NB_START_EPOCHS = 20

model = Sequential()
model.add(Dense(64, input_shape=(NB_WORDS,), activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(len(classes), activation='softmax'))

def deep_model(model, X_train, y_train, X_valid, y_valid):
    model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])
    history = model.fit(X_train, y_train, epochs=NB_START_EPOCHS, batch_size=BATCH_SIZE, validation_data=(X_valid, y_valid), verbose=1)
    return history

def optimal_epoch(model_hist):
    min_epoch = np.argmin(model_hist.history['val_loss']) + 1
    print("Minimum validation loss reached in epoch {}".format(min_epoch))
    return min_epoch

base_history = deep_model(model, X_train_rest, y_train_rest, X_valid, y_valid)
base_min = optimal_epoch(base_history)

def eval_metric(model, history, metric_name):
    metric = history.history[metric_name]
    val_metric = history.history['val_' + metric_name]
    e = range(1, NB_START_EPOCHS + 1)
    plt.plot(e, metric, 'bo', label='Train ' + metric_name)
    plt.plot(e, val_metric, 'b', label='Validation ' + metric_name)
    plt.xlabel('Epoch number')
    plt.ylabel(metric_name)
    plt.title('Comparing training and validation ' + metric_name + ' for ' + model.name)
    plt.legend()
    plt.show()

def test_model(model, X_train, y_train, X_test, y_test, epoch_stop):
    model.fit(X_train, y_train, epochs=epoch_stop, batch_size=BATCH_SIZE, verbose=1)
    results = model.evaluate(X_test, y_test)
    print()
    print('Test accuracy: {0:.2f}%'.format(results[1]*100))
    return results

eval_metric(model, base_history, 'loss')

base_results = test_model(model, X_train_oh, y_train_oh, X_test_oh, y_test_oh, base_min)

# Confusion matrix
from sklearn.metrics import confusion_matrix
import seaborn as sns

y_pred = model.predict(X_test_oh)
cm = confusion_matrix(np.argmax(y_test_oh, axis=1), np.argmax(y_pred, axis=1))

sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
plt.title('Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.show()

print(classification_report(np.argmax(y_test_oh, axis=1), np.argmax(y_pred, axis=1), target_names=classes))

reduced_model = Sequential()
reduced_model.add(Dense(16, activation='relu', input_shape=(NB_WORDS,)))
reduced_model.add(Dense(3, activation='softmax'))
reduced_model.summary()

reduced_history = deep_model(reduced_model, X_train_rest, y_train_rest, X_valid, y_valid)
reduced_min = optimal_epoch(reduced_history)

eval_metric(reduced_model, reduced_history, 'loss')

reduced_results = test_model(reduced_model, X_train_oh, y_train_oh, X_test_oh, y_test_oh, base_min)

def compare_models_by_metric(model_1, model_2, model_hist_1, model_hist_2, metric):

    metric_model_1 = model_hist_1.history[metric]
    metric_model_2 = model_hist_2.history[metric]

    e = range(1, NB_START_EPOCHS + 1)
    
    metrics_dict = {
        'acc' : 'Training Accuracy',
        'loss' : 'Training Loss',
        'val_acc' : 'Validation accuracy',
        'val_loss' : 'Validation loss'
    }
    
    metric_label = metrics_dict[metric]

    plt.plot(e, metric_model_1, 'bo', label=model_1.name)
    plt.plot(e, metric_model_2, 'b', label=model_2.name)
    plt.xlabel('Epoch number')
    plt.ylabel(metric_label)
    plt.title('Comparing ' + metric_label + ' between models')
    plt.legend()
    plt.show()

compare_models_by_metric(model, reduced_model, base_history, reduced_history, 'val_loss')

from sklearn.metrics import confusion_matrix
import seaborn as sns

y_pred = reduced_model.predict(X_test_oh)
cm = confusion_matrix(np.argmax(y_test_oh, axis=1), np.argmax(y_pred, axis=1))

sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
plt.title('Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.show()

from keras import regularizers

reg_model = Sequential()
reg_model.add(Dense(64, kernel_regularizer=regularizers.l2(0.001), activation='relu', input_shape=(NB_WORDS,)))
reg_model.add(Dense(64, kernel_regularizer=regularizers.l2(0.001), activation='relu'))
reg_model.add(Dense(3, activation='softmax'))
reg_model.summary()

reg_history = deep_model(reg_model, X_train_rest, y_train_rest, X_valid, y_valid)
reg_min = optimal_epoch(reg_history)

eval_metric(reg_model, reg_history, 'loss')

reg_results = test_model(reg_model, X_train_oh, y_train_oh, X_test_oh, y_test_oh, base_min)

from sklearn.metrics import confusion_matrix
import seaborn as sns

y_pred = reg_model.predict(X_test_oh)
cm = confusion_matrix(np.argmax(y_test_oh, axis=1), np.argmax(y_pred, axis=1))

sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
plt.title('Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.show()

drop_model = Sequential()
drop_model.add(Dense(64, activation='relu', input_shape=(NB_WORDS,)))
drop_model.add(Dropout(0.5))
drop_model.add(Dense(64, activation='relu'))
drop_model.add(Dropout(0.5))
drop_model.add(Dense(3, activation='softmax'))
drop_model.summary()

drop_history = deep_model(drop_model, X_train_rest, y_train_rest, X_valid, y_valid)
drop_min = optimal_epoch(drop_history)

eval_metric(drop_model, drop_history, 'loss')

drop_results = test_model(drop_model, X_train_oh, y_train_oh, X_test_oh, y_test_oh, base_min)

compare_models_by_metric(model, drop_model, base_history, drop_history, 'val_loss')

from sklearn.metrics import confusion_matrix
import seaborn as sns

y_pred = drop_model.predict(X_test_oh)
cm = confusion_matrix(np.argmax(y_test_oh, axis=1), np.argmax(y_pred, axis=1))

sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
plt.title('Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.show()

reduce_dropout_model = Sequential()
reduce_dropout_model.add(Dense(16, activation='relu', input_shape=(NB_WORDS,)))
reduce_dropout_model.add(Dropout(0.5))
reduce_dropout_model.add(Dense(3, activation='softmax'))
reduce_dropout_model.summary()

reduce_drop_history = deep_model(reduce_dropout_model, X_train_rest, y_train_rest, X_valid, y_valid)
reduce_drop_min = optimal_epoch(reduce_drop_history)

eval_metric(reduce_dropout_model, reduce_drop_history, 'loss')

reduce_dropout_results = test_model(reduce_dropout_model, X_train_oh, y_train_oh, X_test_oh, y_test_oh, base_min)

compare_models_by_metric(model, reduce_dropout_model, base_history, reduce_drop_history, 'val_loss')

y_pred = reduce_dropout_model.predict(X_test_oh)
cm = confusion_matrix(np.argmax(y_test_oh, axis=1), np.argmax(y_pred, axis=1))

sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
plt.title('Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.show()