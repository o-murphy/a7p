__version__ = '0.0.8'
__author__ = "o-murphy"
__credits__ = ["Dmytro Yaroshenko"]
__copyright__ = ("",)

try:
    from a7p import profedit_pb2, factory
    from a7p import protovalidate as validator
    from a7p.a7p import A7PFile, A7PDataError
    from a7p.profedit_pb2 import *
    from a7p.factory import A7PFactory
except ImportError:
    import logging
    logging.warning("Can't import 'google' or 'protobuf' package, pass it on setup")

__all__ = ['A7PFile', 'A7PDataError', 'A7PFactory', 'factory',
           'profedit_pb2',
           'Payload', 'Profile', 'DType', 'GType', 'TwistDir', 'SwPos', 'CoefRow']
