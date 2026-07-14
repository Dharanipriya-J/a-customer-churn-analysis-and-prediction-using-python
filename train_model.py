import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle

df=pd.read_csv("dataset.csv")

df['gender_num']=df['gender'].apply(
lambda x:1 if x=="Male" else 0
)

pay_map={
"Credit Card":0,
"Debit Card":1,
"UPI":2,
"Net Banking":3
}

df['payment_num']=df['payment_method'].map(pay_map)

X=df[[
'gender_num',
'tenure',
'monthly',
'total',
'payment_num'
]]

y=df['churn']

X_train,X_test,y_train,y_test=train_test_split(
X,
y,
test_size=0.2,
random_state=42
)

model=RandomForestClassifier(n_estimators=100)

model.fit(X_train,y_train)

accuracy=model.score(X_test,y_test)

print("Model Accuracy:",accuracy)

pickle.dump(model,open("model.pkl","wb"))

print("Model trained successfully")