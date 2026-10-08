from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .schema import model_columns


def build_preprocessor(frame):
    columns = model_columns(list(frame.columns))
    numeric = frame[columns].select_dtypes(include="number").columns.tolist()
    categorical = [column for column in columns if column not in numeric]
    numeric_pipeline = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    categorical_pipeline = Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("encode", OneHotEncoder(handle_unknown="ignore"))])
    return ColumnTransformer([("numeric", numeric_pipeline, numeric), ("categorical", categorical_pipeline, categorical)])
