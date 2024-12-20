

if __name__ == '__main__':
    from a7p import load
    from a7p.exceptions import A7PProtoValidationError, _extract_protovalidate_violations

    # Main execution block
    with open(r"./broken.a7p", 'rb') as fp:
        try:
            a7p = load(fp, validate_=True)
        except A7PProtoValidationError as e:
            for v in e.violations:
                print(f"Field Path: {v.path}")
                print(f"Constraint ID: {v.value}")
                print(f"Message: {v.reason}")
                print("---")
