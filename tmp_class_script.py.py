#!/usr/bin/env python
# coding: utf-8

# # Classification from Regression Benchmark + DNNs
# 
# This notebook demonstrates how to reuse the models/families from `Regression_Benchmark_25Methods.ipynb` and the DNN architectures from `Deep_Neural_Learning_Modeling.ipynb` for a classification task. It provides:
# 
# - a mapping from regressors -> classifier equivalents,
# - a preprocessing pipeline compatible with both classical models and Keras DNNs,
# - an adapted DNN builder for classification (softmax/sigmoid outputs),
# - an example workflow to train/evaluate a set of classifiers and the DNNs (intended to run in Colab / TF-capable env).

# ## Notes
# 
# - This notebook is intentionally framework-agnostic: it reuses algorithm families from the regression benchmark but uses classifier implementations.
# - The DNN builder is an adaptation of the DNNs in `Deep_Neural_Learning_Modeling.ipynb`; change `num_classes` to match your problem and pick `loss`/`activation` accordingly.
# - For heavy DNN runs use Google Colab (GPU) or a macOS Python 3.10 env with `tensorflow-macos` + `tensorflow-metal` on Apple Silicon.

# In[15]:


# Standard imports
import os
import numpy as np
import pandas as pd
import random
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
# classical classifiers
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import LinearSVC, SVC
# try to import other libraries (xgboost, lightgbm, catboost) if available
try:
    from xgboost import XGBClassifier
except Exception:
    XGBClassifier = None
try:
    from lightgbm import LGBMClassifier
except Exception:
    LGBMClassifier = None
try:
    from catboost import CatBoostClassifier
except Exception:
    CatBoostClassifier = None
# Keras for DNNs
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    KERAS_AVAILABLE = True
except Exception:
    KERAS_AVAILABLE = False

# Reproducibility helper
SEED = 42
np.random.seed(SEED)
random.seed(SEED)
os.environ.setdefault('PYTHONHASHSEED', str(SEED))


# ### DNN builder (adapted for classification)
# The following builder creates three kinds of DNN bodies: 'mlp', 'deep_mlp', 'cnn'. It adapts the final layer and loss for classification (binary or multiclass).

# In[16]:


if KERAS_AVAILABLE:

    def build_classification_dnn(kind, input_shape, num_classes, dropout=0.3, use_batchnorm=True, lr=1e-3):
        inputs = keras.Input(shape=(input_shape,))
        x = inputs
        if kind == 'mlp':
            x = layers.Dense(256, activation='relu')(x)
            if use_batchnorm: x = layers.BatchNormalization()(x)
            x = layers.Dropout(dropout)(x)
            x = layers.Dense(128, activation='relu')(x)
        elif kind == 'deep_mlp':
            x = layers.Dense(512, activation='relu')(x)
            if use_batchnorm: x = layers.BatchNormalization()(x)
            x = layers.Dropout(dropout)(x)
            x = layers.Dense(256, activation='relu')(x)
            if use_batchnorm: x = layers.BatchNormalization()(x)
            x = layers.Dropout(dropout)(x)
            x = layers.Dense(128, activation='relu')(x)
        elif kind == 'cnn':
            # treat features as a 1D sequence: reshape then Conv1D
            x = layers.Reshape((input_shape, 1))(x)
            x = layers.Conv1D(64, 3, activation='relu', padding='same')(x)
            if use_batchnorm: x = layers.BatchNormalization()(x)
            x = layers.Conv1D(32, 3, activation='relu', padding='same')(x)
            x = layers.GlobalMaxPooling1D()(x)
            x = layers.Dense(64, activation='relu')(x)
        else:
            raise ValueError('Unknown kind: ' + str(kind))

        if num_classes == 2:
            outputs = layers.Dense(1, activation='sigmoid')(x)
            loss = 'binary_crossentropy'
            metrics = ['accuracy']
        else:
            outputs = layers.Dense(num_classes, activation='softmax')(x)
            loss = 'sparse_categorical_crossentropy'
            metrics = ['accuracy']

        model = keras.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer=keras.optimizers.Adam(learning_rate=lr), loss=loss, metrics=metrics)
        return model

else:
    def build_classification_dnn(*args, **kwargs):
        raise RuntimeError('Keras/TensorFlow not available in this environment')


# ## Models dictionary (classification equivalents)
# The following dictionary assembles a representative set of classifiers (10+ methods) adapted from the regression notebook.

# In[17]:


def get_classification_models(random_state=SEED):
    models = {
        'LogisticRegression': LogisticRegression(max_iter=1000, random_state=random_state),
        'RandomForest': RandomForestClassifier(n_estimators=200, random_state=random_state),
        'ExtraTrees': ExtraTreesClassifier(n_estimators=200, random_state=random_state),
        'GradientBoosting': GradientBoostingClassifier(n_estimators=200, random_state=random_state),
        'DecisionTree': DecisionTreeClassifier(random_state=random_state),
        'KNeighbors': KNeighborsClassifier(),
        'GaussianNB': GaussianNB(),
        'LinearSVC': LinearSVC(max_iter=5000, random_state=random_state),
        'AdaBoost': AdaBoostClassifier(n_estimators=100, random_state=random_state),
    }
    if XGBClassifier is not None:
        models['XGBoost'] = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=random_state)
    if LGBMClassifier is not None:
        models['LightGBM'] = LGBMClassifier(random_state=random_state)
    if CatBoostClassifier is not None:
        models['CatBoost'] = CatBoostClassifier(verbose=0, random_state=random_state)
    return models


# ## Example workflow (load data, preprocess, quick fit)
# The following cell demonstrates how to wire preprocessing + classifiers + DNN. It intentionally runs a quick smoke-fit for classical models. For full DNN training switch to Colab or a TF-capable env and set `RUN_DNNS=True`.

# In[18]:


# Configuration
RUN_DNNS = False  # set True in Colab or TF-capable env to run DNNs
DATA_PATH = 'demand_forecasting_dataset.csv'  # change to your dataset or load the Walmart dataset used elsewhere
TARGET = 'target'  # replace with your target column name

# Try to load a dataset if present (non-fatal)
if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
    print('Loaded', DATA_PATH, 'shape=', df.shape)
else:
    df = None

# Example: if df is provided, create 3-class target by tertiles (mirrors Classification_Walmart.ipynb)
if df is not None and TARGET in df.columns:
    q1 = df[TARGET].quantile(1/3)
    q2 = df[TARGET].quantile(2/3)
    print('Tertile thresholds:', q1, q2)
    def tertile_label(v):
        if v <= q1: return 0
        if v <= q2: return 1
        return 2
    df['y_class'] = df[TARGET].apply(tertile_label)
    y = df['y_class']
    X = df.drop(columns=[TARGET, 'y_class'])
    preprocessor, numeric_cols, categorical_cols = build_preprocessor(X)
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.4, stratify=y, random_state=SEED)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=SEED)

    # build models and run a quick classical fit (short)
    models = get_classification_models()
    results = {}
    for name, m in models.items():
        pipe = Pipeline([('pre', preprocessor), ('model', m)])
        try:
            pipe.fit(X_train, y_train)
            preds = pipe.predict(X_val)
            acc = accuracy_score(y_val, preds)
            results[name] = acc
            print(f'{name}: val accuracy = {acc:.4f}')
        except Exception as e:
            print('Failed', name, '->', e)

    # DNN training (optional)
    if RUN_DNNS and KERAS_AVAILABLE:
        # process features to numpy arrays
        X_train_trans = preprocessor.fit_transform(X_train)
        X_val_trans = preprocessor.transform(X_val)
        input_shape = X_train_trans.shape[1]
        num_classes = len(np.unique(y_train))
        # example: train MLP quickly (for demonstration only)
        model = build_classification_dnn('mlp', input_shape=input_shape, num_classes=num_classes, dropout=0.3)
        history = model.fit(X_train_trans, y_train, validation_data=(X_val_trans, y_val), epochs=10, batch_size=32)
        print('DNN trained (demo)')

else:
    if df is None:
        print('No DATA_PATH found. Edit DATA_PATH and TARGET to run this notebook on your data.')
    else:
        print('Data loaded but TARGET not found or RUN_DNNS=False; classical models attempted if possible.')


# ## How to run DNNs (Colab recommended)
# - Upload this notebook to Colab, set Runtime -> GPU, set `RUN_DNNS = True` in the configuration cell, then run all cells.
# - If you prefer local runs on Apple Silicon, create a Python 3.10 venv and install `tensorflow-macos` + `tensorflow-metal` before running. The rest of the pipeline (scikit-learn models) works on your current venv.
