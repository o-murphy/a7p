from a7p import A7PFile

with open("308W_GGG 175GR SMK_2024_10_08_09_54_36_prof.a7p", "rb") as fp:

    payload = A7PFile.load(fp, validate=True)
    print(payload.profile.c_zero_air_pressure)

# del payload.profile.coef_rows[:]
# # payload.profile.coef_rows.append([])
#
# with open("velocity.a7p", "wb") as fp:
#     A7PFile.dump(payload, fp, False)

import argparse


parser = argparse.ArgumentParser()

parser.add_argument()