from a7p import A7PFile

with open("test.a7p", "rb") as fp:

    payload = A7PFile.load(fp, validate=True)
    print(payload.profile.c_zero_air_pressure)

del payload.profile.distances[:]
# payload.profile.coef_rows.append([])

with open("broken.a7p", "wb") as fp:
    A7PFile.dump(payload, fp, False)
