class OcrError(Exception):
    def __init__(self, message="Cannot read an image"):
        super().__init__(message)

class ParsingError(Exception):
  def __init__(self, message="Cannot parse the receipt"):
        super().__init__(message)