# ML Benchmark: Classification, Clustering, and Sentiment Analysis on Waltermart Dataset

This document outlines a comprehensive benchmark study using the Waltermart sales dataset, expanding on the previous regression analysis. It covers three major ML tasks: classification, unsupervised learning (clustering/dimensionality reduction), and sentiment analysis, each with a diverse set of methods including deep neural networks.

---

## 1. Classification (at least 10 unique methods, 3+ DNNs)

**Objective:** Predict categorical outcomes (e.g., high/low sales, store type, or holiday vs non-holiday week) using the Waltermart dataset.

**Methods:**
- Logistic Regression
- Random Forest Classifier
- Gradient Boosting Classifier
- Support Vector Machine (SVC)
- K-Nearest Neighbors (KNN)
- Naive Bayes (GaussianNB)
- Decision Tree Classifier
- XGBoost Classifier
- LightGBM Classifier
- CatBoost Classifier
- Deep Neural Networks (MLP, CNN, LSTM)

**DNNs:**
- MLP Classifier (Keras/TensorFlow)
- CNN Classifier (Keras/TensorFlow)
- LSTM Classifier (Keras/TensorFlow)

**Relation to Regression:**
- Use engineered features from regression (lag, rolling, time, interaction)
- Target can be binarized (e.g., above/below median sales)
- Same preprocessing pipeline

---

## 2. Unsupervised Learning (at least 10 unique methods)

**Objective:** Discover patterns, clusters, or reduce dimensionality in Waltermart data (e.g., group stores/weeks, find sales patterns).

**Methods:**
- K-Means Clustering
- Agglomerative Clustering
- DBSCAN
- Gaussian Mixture Model
- Spectral Clustering
- Birch Clustering
- MiniBatch K-Means
- Mean Shift
- Principal Component Analysis (PCA)
- t-SNE
- UMAP
- Autoencoder (DNN)
- Self-Organizing Map (SOM, DNN)

**Relation to Regression:**
- Use same feature set
- Cluster stores/weeks based on sales and engineered features
- Dimensionality reduction for visualization or preprocessing

---

## 3. Sentiment Analysis (at least 6 unique methods)

**Objective:** Analyze textual data (e.g., customer reviews, store feedback, or social media posts related to Waltermart) for sentiment polarity.

**Methods:**
- VADER (rule-based)
- TextBlob (rule-based)
- Logistic Regression (on TF-IDF features)
- SVM (on TF-IDF features)
- Random Forest (on TF-IDF features)
- Naive Bayes (on TF-IDF features)
- Deep Neural Network (MLP on embeddings)
- LSTM (on word embeddings)
- Transformer-based (BERT, DistilBERT)

**Relation to Regression:**
- Sentiment scores can be used as additional features in regression/classification
- Can analyze customer feedback for weeks with high/low sales

---

## 4. Data and Feature Engineering
- All tasks use the Waltermart sales dataset
- Feature engineering from regression (lag, rolling, time, interaction) is reused
- For sentiment analysis, external text data (e.g., reviews) is assumed to be available or simulated

---

## 5. Summary Table
| Task                | Methods Used (Count) | DNNs Included | Data Source         |
|---------------------|----------------------|---------------|--------------------|
| Classification      | 10+                  | 3+            | Waltermart sales   |
| Unsupervised        | 10+                  | 2+            | Waltermart sales   |
| Sentiment Analysis  | 6+                   | 2+            | Reviews/Feedback   |

---

## 6. Discussion
- This benchmark extends the regression study by applying classification, clustering, and sentiment analysis to the same dataset and engineered features.
- Deep learning models are included for each task, ensuring modern ML coverage.
- Results from each task can be cross-referenced (e.g., clusters with high sales, sentiment impact on sales).
- The workflow supports publication-quality analysis and can be implemented in Python (scikit-learn, TensorFlow, PyTorch, HuggingFace).

---

## 7. Next Steps
- Prepare code notebooks for each task
- Run benchmarks and compare performance
- Integrate findings into a unified report
- Use sentiment and cluster results as features for advanced regression/classification

---

# ML Benchmark: Classification, Clustering, and Sentiment Analysis on Waltermart Dataset

# ---
# 1. Classification (10+ methods, 3+ DNNs)
# --------------------------------------------------
# This section uses the Waltermart sales dataset and engineered features from regression.
# The target is binarized (high/low sales) for classification. All models use the same features.

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

# Load Waltermart sales data
# (Assume feature_cols are engineered as in regression notebook)
df = pd.read_csv('walmart-sales-dataset-of-45stores.csv')
# ...feature engineering as in regression notebook...

# Create binary target: High vs Low sales
median_sales = df['Weekly_Sales'].median()
df['HighSales'] = (df['Weekly_Sales'] > median_sales).astype(int)
X = df[feature_cols].copy()
y = df['HighSales']

# Split and scale
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# --- Classical classifiers ---
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

models = [
    ('LogisticRegression', LogisticRegression()),
    ('RandomForest', RandomForestClassifier()),
    ('GradientBoosting', GradientBoostingClassifier()),
    ('AdaBoost', AdaBoostClassifier()),
    ('SVC', SVC()),
    ('KNN', KNeighborsClassifier()),
    ('NaiveBayes', GaussianNB()),
    ('DecisionTree', DecisionTreeClassifier()),
    ('XGBoost', XGBClassifier(use_label_encoder=False, eval_metric='logloss')),
    ('LightGBM', LGBMClassifier()),
    ('CatBoost', CatBoostClassifier(verbose=0))
]

results = {}
for name, model in models:
    # Fit and evaluate each classifier
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    results[name] = accuracy_score(y_test, y_pred)

print('Classification Results:', results)

# --- Deep Neural Networks (MLP, CNN, LSTM) ---
from keras.models import Sequential
from keras.layers import Dense, Dropout, BatchNormalization, Conv1D, Flatten, LSTM

# MLP Classifier
mlp = Sequential([
    Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    BatchNormalization(),
    Dropout(0.3),
    Dense(64, activation='relu'),
    Dense(1, activation='sigmoid')
])
mlp.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
mlp.fit(X_train, y_train, epochs=30, batch_size=32, validation_split=0.2, verbose=0)
mlp_acc = mlp.evaluate(X_test, y_test, verbose=0)[1]

# CNN Classifier
X_train_cnn = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
X_test_cnn = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))
cnn = Sequential([
    Conv1D(64, 3, activation='relu', input_shape=(X_train.shape[1], 1)),
    BatchNormalization(),
    Flatten(),
    Dense(64, activation='relu'),
    Dense(1, activation='sigmoid')
])
cnn.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
cnn.fit(X_train_cnn, y_train, epochs=30, batch_size=32, validation_split=0.2, verbose=0)
cnn_acc = cnn.evaluate(X_test_cnn, y_test, verbose=0)[1]

# LSTM Classifier
X_train_lstm = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))
X_test_lstm = X_test.reshape((X_test.shape[0], 1, X_test.shape[1]))
lstm = Sequential([
    LSTM(64, input_shape=(1, X_train.shape[1])),
    Dense(1, activation='sigmoid')
])
lstm.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
lstm.fit(X_train_lstm, y_train, epochs=30, batch_size=32, validation_split=0.2, verbose=0)
lstm_acc = lstm.evaluate(X_test_lstm, y_test, verbose=0)[1]

print('MLP Accuracy:', mlp_acc)
print('CNN Accuracy:', cnn_acc)
print('LSTM Accuracy:', lstm_acc)

# ---
# 2. Unsupervised Learning (10+ methods)
# --------------------------------------------------
# Uses regression features to cluster and reduce dimensionality of Waltermart data.

from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN, Birch, MeanShift, SpectralClustering, MiniBatchKMeans
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap

X = df[feature_cols].copy()
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# --- Clustering methods ---
cluster_methods = [
    ('KMeans', KMeans(n_clusters=5)),
    ('Agglomerative', AgglomerativeClustering(n_clusters=5)),
    ('DBSCAN', DBSCAN(eps=0.5)),
    ('Birch', Birch(n_clusters=5)),
    ('MeanShift', MeanShift()),
    ('Spectral', SpectralClustering(n_clusters=5)),
    ('MiniBatchKMeans', MiniBatchKMeans(n_clusters=5)),
    ('GaussianMixture', GaussianMixture(n_components=5))
]

cluster_results = {}
for name, method in cluster_methods:
    # Fit and get cluster labels
    labels = method.fit_predict(X_scaled)
    cluster_results[name] = labels

# --- Dimensionality reduction ---
pca = PCA(n_components=2).fit_transform(X_scaled)  # Principal Component Analysis
tsne = TSNE(n_components=2).fit_transform(X_scaled)  # t-SNE
umap_emb = umap.UMAP(n_components=2).fit_transform(X_scaled)  # UMAP

# --- DNN: Autoencoder for unsupervised embedding ---
from keras.layers import Input
from keras.models import Model
input_dim = X_scaled.shape[1]
encoding_dim = 5
input_layer = Input(shape=(input_dim,))
encoded = Dense(encoding_dim, activation='relu')(input_layer)
decoded = Dense(input_dim, activation='linear')(encoded)
autoencoder = Model(input_layer, decoded)
autoencoder.compile(optimizer='adam', loss='mse')
autoencoder.fit(X_scaled, X_scaled, epochs=30, batch_size=32, verbose=0)
embeddings = autoencoder.predict(X_scaled)

print('Clustering and Embedding Results Ready.')

# ---
# 3. Sentiment Analysis (6+ methods)
# --------------------------------------------------
# Assumes you have a DataFrame 'reviews_df' with ['review_text', 'label'] for Waltermart reviews.
# Sentiment scores can be used as features in regression/classification.

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Example: reviews_df = pd.read_csv('waltermart_reviews.csv')
X_text = reviews_df['review_text']
y_sent = reviews_df['label']  # 1=positive, 0=negative

X_train, X_test, y_train, y_test = train_test_split(X_text, y_sent, test_size=0.2, random_state=42)
vectorizer = TfidfVectorizer(max_features=1000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# --- Classical ML for sentiment ---
models = [
    ('LogisticRegression', LogisticRegression()),
    ('SVC', SVC()),
    ('RandomForest', RandomForestClassifier()),
    ('NaiveBayes', MultinomialNB())
]
for name, model in models:
    # Fit and evaluate sentiment classifier
    model.fit(X_train_vec, y_train)
    print(f'{name} accuracy:', model.score(X_test_vec, y_test))

# --- Rule-based sentiment ---
analyzer = SentimentIntensityAnalyzer()
vader_scores = [analyzer.polarity_scores(t)['compound'] for t in X_test]
textblob_scores = [TextBlob(t).sentiment.polarity for t in X_test]

# --- DNN: MLP for sentiment ---
from keras.models import Sequential
from keras.layers import Dense, Dropout
mlp = Sequential([
    Dense(128, activation='relu', input_shape=(X_train_vec.shape[1],)),
    Dropout(0.3),
    Dense(1, activation='sigmoid')
])
mlp.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
mlp.fit(X_train_vec.toarray(), y_train, epochs=10, batch_size=32, verbose=0)
mlp_acc = mlp.evaluate(X_test_vec.toarray(), y_test, verbose=0)[1]
print('MLP Sentiment Accuracy:', mlp_acc)

# --- Transformer-based (BERT, optional) ---
# from transformers import pipeline
# sentiment_pipeline = pipeline('sentiment-analysis')
# bert_results = sentiment_pipeline(list(X_test)[:10])

# ---
# All code uses the Waltermart dataset and engineered features from your regression analysis.
# You can expand each section for deeper analysis or publication.
