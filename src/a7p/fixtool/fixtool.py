from email.policy import default

from google._upb._message import RepeatedScalarContainer


class FixTool:
    def __init__(self):
        self.fixtools = {}

    def register(self, path, func):
        self.fixtools[path] = func

    @staticmethod
    def get_value_by_violation(payload, violation):
        _value = payload
        _path = violation.path.split('.')
        for p in _path:
            if hasattr(_value, p):
                _value = getattr(_value, p)
        if isinstance(_value, (RepeatedScalarContainer, list, tuple)):
            _value = [str(v) for v in _value]
            if len(_value) > 6:
                _value = f'[ {", ".join(_value[:3])}, ... {", ".join(_value[-3:])} ]'
            else:
                _value = f'[ {",".join(_value)} ]'
            # if len(_value) > 50:
            #     _value = f'[ {_value[:25]} ... {_value[-25:]} ]'
        return _value

    def fix_one(self, payload, violation):
        if violation.path in self.fixtools:
            old_value = self.get_value_by_violation(payload, violation)
            self.fixtools[violation.path](payload)
            new_value = self.get_value_by_violation(payload, violation)

            prefix = f"Fixed: {violation.path}"
            prefix = prefix.ljust(40)  # Reassign the result of rjust() to prefix
            if len(prefix) > 40:
                prefix = prefix[:37] + "..."
            print(f"{prefix}\t|\tvalue changed: {old_value} -> {new_value}")
            return True
        print(violation.format())
        return False

    def fix(self, payload, violations):
        total = len(violations)
        skipped = 0
        for v in violations:
            if not self.fix_one(payload, v):
                skipped += 1
        print(f"Total {total}, Fixed: {total - skipped}, Skipped: {skipped}")