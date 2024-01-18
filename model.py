import sqlite3
import time
from io import StringIO

import pandas as pd

import cudf
from cuml.neighbors import KNeighborsClassifier


class ModelManager:

    def __init__(self):
        dbname = './data/point220.sqlite3'
        conn = sqlite3.connect(dbname)
        cur = conn.cursor()

        pf = pd.read_sql('SELECT * FROM point', conn)

        cur.close()
        conn.close()

        X_panda = pf.iloc[:, 2:6]
        print(X_panda)
        y_panda = pf['group_id']
        X = cudf.DataFrame.from_pandas(X_panda)

        self.knn = KNeighborsClassifier(n_neighbors=1)

        train_start = time.process_time()
        print("Training kNN Model...")
        self.knn.fit(X, y_panda)

        print(f"Train ended {time.process_time() - train_start}s")

    def predict(self, points):
        data = StringIO(f"""{int(points["ap1_rtt"])},{int(points["ap2_rtt"])},{int(points["ap3_rtt"])},{int(points["ap4_rtt"])}""")
        pf = pd.read_csv(data, header=None)
        X = cudf.DataFrame.from_pandas(pf)
        print(X)
        ans = self.knn.predict(X)

        return ans