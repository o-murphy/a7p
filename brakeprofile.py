from a7p import A7PFile

with open("a7p/test.a7p", "rb") as fp:

    payload = A7PFile.load(fp, validate=True)

del payload.profile.distances[:]
payload.profile.b_weight = 2000000
payload.profile.c_muzzle_velocity = 100000
payload.profile.short_name_top = "abcdefghij"
# payload.profile.coef_rows.append([])

with open("broken.a7p", "wb") as fp:
    A7PFile.dump(payload, fp, False)