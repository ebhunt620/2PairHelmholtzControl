import csv
import numpy as np
from datetime import datetime
f = open("some.csv", "wb")
writer = csv.writer(f)
x = np.array([1, 2, 3, 4])
writer.writerows([x])
f.close()


