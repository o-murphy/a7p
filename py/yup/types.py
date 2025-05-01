from typing_extensions import Callable, Any

__all__ = ('TransformFunc', 'ValidatorFunc')

TransformFunc = Callable[[Any], Any]
ValidatorFunc = Callable[[Any], None]
