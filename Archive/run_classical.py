import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier, ExtraTreesClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier

# Load
df = pd.read_csv('walmart-sales-dataset-of-45stores.csv')
# Label
quantiles = df['Weekly_Sales'].quantile([0.33,0.66]).values
q1,q2 = quantiles[0], quantiles[1]

def sales_to_class(x):
    if x <= q1:
        return 0
    elif x <= q2:
        return 1
    else:
        return 2

df['sales_class'] = df['Weekly_Sales'].apply(sales_to_class)

# Split
X = df.drop(columns=['sales_class'])
y = df['sales_class']
X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.25, random_state=42, stratify=y_temp)

# Features
num_cols = X_train.select_dtypes(include=['int64','float64']).columns.tolist()
cat_cols = X_train.select_dtypes(include=['object','category']).columns.tolist()
for col in ['Date','Weekly_Sales']:
    if col in num_cols:
        num_cols.remove(col)

numeric_transformer = Pipeline(steps=[('scaler', StandardScaler())])
try:
    categorical_transformer = Pipeline(steps=[('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))])
except TypeError:
    categorical_transformer = Pipeline(steps=[('onehot', OneHotEncoder(handle_unknown='ignore', sparse=False))])

preprocessor = ColumnTransformer(transformers=[('num', numeric_transformer, num_cols), ('cat', categorical_transformer, cat_cols)])

# Models
models = {
    'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42),
    'RandomForest': RandomForestClassifier(n_estimators=200, random_state=42),
    'ExtraTrees': ExtraTreesClassifier(n_estimators=200, random_state=42),
    'GradientBoosting': GradientBoostingClassifier(random_state=42),
    'AdaBoost': AdaBoostClassifier(random_state=42),
    'KNN': KNeighborsClassifier(n_neighbors=5),
    'LinearSVC': LinearSVC(max_iter=5000, random_state=42),
    'NaiveBayes': GaussianNB(),
    'DecisionTree': DecisionTreeClassifier(random_state=42)
}

# optional XGBoost
try:
    from xgboost import XGBClassifier
    models['XGBoost'] = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)
except Exception:
    pass

# Dense transformer
from sklearn.base import TransformerMixin, BaseEstimator
class DenseTransformer(TransformerMixin, BaseEstimator):
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        if hasattr(X, 'toarray'):
            return X.toarray()
        return np.asarray(X)

# Train
results = []
for name, model in models.items():
    if isinstance(model, GaussianNB):
        pipe = Pipeline(steps=[('preprocessor', preprocessor), ('to_dense', DenseTransformer()), ('clf', model)])
    else:
        pipe = Pipeline(steps=[('preprocessor', preprocessor), ('clf', model)])
    print('Training', name)
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_val)
    acc = accuracy_score(y_val, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_val, y_pred, average='weighted')
    results.append({'Method': name, 'Accuracy': acc, 'Precision': prec, 'Recall': rec, 'F1': f1})

results_df = pd.DataFrame(results).sort_values('F1', ascending=False)
results_df.to_csv('classification_results_classical_validation.csv', index=False)
print('Saved classification_results_classical_validation.csv')

# Save hyperparameters simple logging
hyperparams = {name: getattr(m, 'get_params', lambda: {})() for name, m in models.items()}
hp_rows = [{'Method': name, 'Hyperparams': str(hyperparams.get(name, {}))} for name in models.keys()]
hp_df = pd.DataFrame(hp_rows)
hp_df.to_csv('classification_hyperparameters.csv', index=False)
print('Saved classification_hyperparameters.csv')
