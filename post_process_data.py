import re

import pandas as pd

df = pd.read_csv("muzzle_velocity_statistics.csv")

df["Bullet Weight (grains)"] = df.apply(lambda x: float(re.search(r".+\((\d+) (\w+)", x["Cartridge (Wb + type)"]).group(1)), axis=1)
df["Bullet Weight (grams)"] = df.apply(lambda x: x["Bullet Weight (grains)"]* 0.06479891, axis=1)
df["Bullet Type"] = df.apply(lambda x: re.search(r".+\((\d+) (\w+)", x["Cartridge (Wb + type)"]).group(2), axis=1)
df["MV (mps)"] = df.apply(lambda x: float(x["MV (fps)"]) * 0.3048, axis=1)
df.to_csv("muzzle_velocity_statistics_improved.csv", index=False)