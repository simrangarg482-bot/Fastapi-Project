import joblib 
import os
import pandas as pd 
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline 
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer 
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score, root_mean_squared_error 
from training.train_utils import DATA_FILE_PATH, MODEL_DIR, MODEL_PATH 

df = pd.read_csv(DATA_FILE_PATH)  
df = df.drop(columns = ['name', 'model', 'edition']) 

X = df.drop(columns= 'selling_price') 
y = df['selling_price']  

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42) 

num_cols = X_train.select_dtypes(include = 'number').columns.tolist()
cat_cols = [col for col in X_train.columns if col not in num_cols]

num_pipe = Pipeline(steps = [
    ('imputer', SimpleImputer(strategy='median')), 
    ('scaler', StandardScaler()) 
])

cat_pipe = Pipeline(steps = [
    ('imputer', SimpleImputer(strategy= 'constant', fill_value= 'missing')), 
    ('one_hot_encoder', OneHotEncoder(handle_unknown= 'ignore', sparse_output= False, drop= 'first'))
]) 

preprocessor = ColumnTransformer(transformers = [
    ('num', num_pipe, num_cols), 
    ('cat', cat_pipe, cat_cols)
])

reg = RandomForestRegressor(
    n_estimators= 10, max_depth = 5, random_state = 42
)

rf_model = Pipeline(steps = [
    ('pre', preprocessor), 
    ('reg', reg)
]) 

rf_model.fit(X_train, y_train) 

os.makedirs(MODEL_DIR, exist_ok= True) 
joblib.dump(rf_model, MODEL_PATH)