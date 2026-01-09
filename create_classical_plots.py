import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier, ExtraTreesClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier

# Load data and results
results_df = pd.read_csv('classification_results_classical_validation.csv')
df = pd.read_csv('walmart-sales-dataset-of-45stores.csv')
# recreate splits and preprocessing used in run_classical.py
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
X = df.drop(columns=['sales_class'])
y = df['sales_class']
from sklearn.model_selection import train_test_split
X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.25, random_state=42, stratify=y_temp)

num_cols = X_train.select_dtypes(include=['int64','float64']).columns.tolist()
for col in ['Date','Weekly_Sales']:
    if col in num_cols:
        num_cols.remove(col)
cat_cols = X_train.select_dtypes(include=['object','category']).columns.tolist()

numeric_transformer = Pipeline(steps=[('scaler', StandardScaler())])
try:
    categorical_transformer = Pipeline(steps=[('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))])
except TypeError:
    categorical_transformer = Pipeline(steps=[('onehot', OneHotEncoder(handle_unknown='ignore', sparse=False))])
preprocessor = ColumnTransformer(transformers=[('num', numeric_transformer, num_cols), ('cat', categorical_transformer, cat_cols)])

# Map method name to estimator
model_map = {
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

try:
    from xgboost import XGBClassifier
    model_map['XGBoost'] = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)
except Exception:
    pass

# Plot F1 bar chart
plt.figure(figsize=(8,6))
plot_df = results_df.sort_values('F1', ascending=False)
sns.barplot(data=plot_df, x='F1', y='Method', palette='viridis')
plt.title('Validation F1 by Method')
plt.tight_layout()
plt.savefig('validation_f1_by_method.png', dpi=300, bbox_inches='tight')
print('Saved validation_f1_by_method.png')

# Best method
best = plot_df.iloc[0]['Method']
print('Best method (validation):', best)

# Fit best model on train and evaluate on test
best_model = model_map.get(best)
from sklearn.base import TransformerMixin, BaseEstimator
class DenseTransformer(TransformerMixin, BaseEstimator):
    def fit(self, X, y=None): return self
    def transform(self, X):
        if hasattr(X, 'toarray'):
            return X.toarray()
        return np.asarray(X)

if isinstance(best_model, GaussianNB):
    pipe = Pipeline(steps=[('preprocessor', preprocessor), ('to_dense', DenseTransformer()), ('clf', best_model)])
else:
    pipe = Pipeline(steps=[('preprocessor', preprocessor), ('clf', best_model)])

pipe.fit(X_train, y_train)
y_test_pred = pipe.predict(X_test)
cm = confusion_matrix(y_test, y_test_pred)
plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Low','Medium','High'], yticklabels=['Low','Medium','High'])
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title(f'Confusion Matrix - {best} on Test')
plt.tight_layout()
plt.savefig('confusion_matrix_best_test.png', dpi=300, bbox_inches='tight')
print('Saved confusion_matrix_best_test.png')
