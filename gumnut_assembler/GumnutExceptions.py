class Error(Exception):

    """
    Base class for all exceptions.

    This is the base class for all exceptions raised within the
    GumnutSimulator context. To provide sufficient user feedback the
    cause expression of the exception and a somewhat helpfull message
    is passed to the constructor.

    :param expression: A string containing the expression which caused
                       the exception to be raised.

    :param message: A string containing some more information what could
                      raise such an exception.
    """

    def __init__(self, expression, message):
        super().__init__()
        self.type = type(self).__name__
        self.expression = expression
        self.message = message

    def __repr__(self):
        return str("Error <", self.type, ", ", self.message, ", ", self.expression, ">")

    def as_dict(self):
        return dict({"type": self.type, "expression": self.expression, "message": self.message})


class InvalidPCValue(Error):

    """
    Get's raised when the programm counter (PC) has an invalid value.
    This is the case for any value less than ``0`` and greater than
    ``4095``.
    """


class InstructionMemorySizeExceeded(Error):

    """
    Get's raised when trying to upload more data into the instruction
    memory than it can hold.
    """


class DataMemorySizeExceeded(Error):

    """
    Get's raised when trying to upload more data into the data memory
    than it can hold.
    """


class DataMemoryAccessViolation(Error):

    """
    Get's raised when trying to access data from the data memory which
    isn't accessible.
    """


class InvalidInstruction(Error):

    """
    Get's raised when an unknown or invalid instruction is encountered.
    """


class EmptyReturnStack(Error):

    """
    Get's raised when trying to return from a subroutine although the
    return address stack is empty.
    """


class ReturnAddressStackOverflow(Error):

    """
    Get's raised when trying jump into a subroutine although the
    return address stack is already full.
    """
