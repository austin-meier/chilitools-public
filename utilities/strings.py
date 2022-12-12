from datetime import datetime

def currentDatetime() -> str:
  return datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")

def convertFileSize(bytesSize: int, unit: str, roundingPlaces: int = 2) -> str:
  unit = unit.lower()

  if unit == 'kb':
    return str(round(bytesSize/1024, roundingPlaces)) + ' Kb'
  if unit == 'mb':
    return str(round(bytesSize/1048576, roundingPlaces)) + ' Mb'
  if unit == 'gb':
    return str(round(bytesSize/1073741824, roundingPlaces)) + ' Gb'
  return bytesSize
