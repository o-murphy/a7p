if __name__ == '__main__':
    from a7p import load
    from a7p.spec_validator import validate_spec
    from a7p.protovalidate import validate as proto_validate
    from a7p.yupy_schema import validate as yupy_validate
    from yupy import ValidationError
    import timeit
    import tqdm
    from pathlib import Path

    with open("../example.a7p", 'rb') as f:
        p = load(f, fail_fast=True)


    def v_old():
        validate_spec(p)


    def v_new():
        yupy_validate(p)


    def v_pro():
        proto_validate(p)


    num = 10
    told = timeit.timeit(v_old, number=num)
    print(told)  # 0.0601s

    tnew = timeit.timeit(v_new, number=num)
    print(tnew)  # 0.0059s

    tpro = timeit.timeit(v_pro, number=num)
    print(tpro)  # 3.4331s

    d = Path('../gallery').rglob("*")
    fs = [p for p in d if p.is_file()]
    errs = []
    for f in tqdm.tqdm(fs):
        with open(f, 'rb') as fp:
            p = load(fp, fail_fast=True, validate_=False)
            try:
                yupy_validate(p, fail_fast=False)
            except ValidationError as err:
                errs.append(err)

    print(len(errs))
    gen = errs[0].errors
    next(gen)

    print(next(gen).invalid_value)

    for e in errs[0].errors:
        print("Violation:")
        print(f"\tPath\t:\t{e.path}")
        print(f"\tValue\t:\t{e.invalid_value!r}")
        print(f"\tReason\t:\t{e.constraint.format_message}")
