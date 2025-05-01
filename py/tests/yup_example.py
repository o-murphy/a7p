from yup import mixed
from yup.validation_error import ValidationError

if __name__ == "__main__":

    s = string().max(5).min(2).lowercase()
    n = number().required().integer().ge(100).le(10).multiple_of(30)
    l = array().required().of(s).min(2)

    s.validate("ab")
    n.validate(60)

    shp = obj().shape(
        {
            "email": string().email().required(),
            "s": s,
            "n": n,
            "shp": obj()
            .shape(
                {
                    "s": s,
                    "n": n,
                    # 'l': l,
                    "o": obj().shape({"n": l}),
                }
            )
            .required(),
        }
    )

    # shp.validate({'s': "ab", 'n': 60})
    try:
        shp.validate(
            {
                "email": "a@gmail.com",
                "s": "wd",
                "n": 60,
                "shp": {"n": "a", "l": ["ab", "b"], "o": {"n": ["g", "g"]}},
            }, False
        )
    except ValidationError as err:

        for e in err.errors:
            print(str(e.path or "<None>") + ':')
            print('  ', e.constraint.format_message)

    m = mixed().one_of(['G1', 'G7'])
    m.validate('F')
