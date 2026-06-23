import pandas as pd
from sklearn.preprocessing import LabelEncoder

df = pd.read_csv("datasets/chronic kidney.csv")

df["classification"] = (
    df["classification"]
    .astype(str)
    .str.strip()
)

le = LabelEncoder()
le.fit(df["classification"])

print(le.classes_)
print(le.transform(le.classes_))