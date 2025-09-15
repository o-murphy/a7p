if __name__ == '__main__':
    from a7p import load
    from a7p.spec_validator import validate_spec
    from a7p.protovalidate import validate as proto_validate
    from a7p.yupy_schema import validate as yupy_validate
    from yupy import ValidationError
    import timeit
    import tqdm
    from pathlib import Path


    # test index switch distance
    with open("example2.a7p", 'rb') as fp:
        p = load(fp, fail_fast=True, validate_=False)
        try:
            yupy_validate(p, fail_fast=False)
        except ValidationError as err:
            for msg in err.messages:
                print(msg)

    d = Path('../a7p-lib/gallery').rglob("*")
    fs = [p for p in d if p.is_file()]
    errs = []
    for f in tqdm.tqdm(fs):
        with open(f, 'rb') as fp:
            p = load(fp, fail_fast=True, validate_=False)
            try:
                yupy_validate(p, fail_fast=False)
            except ValidationError as err:
                errs.append(err)

    print("errs:", len(errs))

    for e in errs[0].errors:
        print("Violation:")
        print(f"\tPath\t:\t{e.path}")
        print(f"\tValue\t:\t{e.invalid_value!r}")
        print(f"\tReason\t:\t{e.constraint.format_message}")

    def speedtest(validator):
        for f in tqdm.tqdm(fs, desc=validator.__name__):
            # with open("example.a7p", 'rb') as fp:
            with open(f, 'rb') as fp:
                p = load(fp, fail_fast=True)
                try:
                    validator(p)
                except ValidationError as err:
                    pass

    def v_old():
        speedtest(validate_spec)

    def v_new():
        speedtest(yupy_validate)

    def v_pro():
        speedtest(proto_validate)

    num = 1
    told = timeit.timeit(v_old, number=num)
    print("spec validator", told)  # 0.0601s

    tnew = timeit.timeit(v_new, number=num)
    print("yupy validator", tnew)  # 0.0059s

    tpro = timeit.timeit(v_pro, number=num)
    print("protovalidate", tpro)  # 3.4331s
