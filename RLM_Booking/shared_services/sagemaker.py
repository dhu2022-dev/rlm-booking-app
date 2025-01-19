import boto3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib
import os

s3_bucket = 'your-s3-bucket-name'
file_key = 'housing.csv'

# Load data from S3
s3 = boto3.client('s3')
obj = s3.get_object(Bucket=s3_bucket, Key=file_key)
df = pd.read_csv(obj['Body'])

# View data
print(df.head())

# Assuming the target column is 'price' and others are features
X = df.drop('price', axis=1)
y = df['price']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
rmse = mean_squared_error(y_test, y_pred, squared=False)
print(f'RMSE: {rmse}')
