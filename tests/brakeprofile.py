import a7p

with open("bc_ok.a7p", "rb") as fp:
    payload = a7p.load(fp, validate_=True)

del payload.profile.distances[:]
payload.profile.distances[:] = [10000000, ]
del payload.profile.switches[3:]
payload.profile.b_weight = 2000000
payload.profile.c_muzzle_velocity = 100000
payload.profile.short_name_top = "abcdefghij"
# payload.profile.c_zero_distance_idx = 100000
# payload.profile.coef_rows.append([])

with open("broken.a7p", "wb") as fp:
    a7p.dump(payload, fp, False)
