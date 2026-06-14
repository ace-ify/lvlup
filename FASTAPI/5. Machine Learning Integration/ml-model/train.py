import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

df = pd.read_csv('housing.csv').iloc[:,:-1].dropna()

X=df.drop(columns='median_house_value')
y=df.median_house_value.copy()

saved_model=LinearRegression().fit(X,y)
joblib.dump(saved_model,'model.joblib')
