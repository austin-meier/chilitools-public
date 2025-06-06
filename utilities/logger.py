import logging, coloredlogs

def getLogger(fullPath: str):
  logger = logging.getLogger(__name__)
  logLevel = logging.INFO

  fmt = '%(asctime)s:%(levelname)s:%(message)s'
  datefmt = '%m/%d/%Y %I:%M:%S %p'
  logFormat = logging.Formatter(fmt, datefmt=datefmt)

  #File logging
  logFile = logging.FileHandler(fullPath)
  logFile.setLevel(logLevel)
  logFile.setFormatter(logFormat)
  logger.addHandler(logFile)

  #Terminal logging
  coloredlogs.install(
    level=logLevel,
    logger=logger,
    fmt=fmt,
    datefmt=datefmt
  )
  return logger

def log_level(level: str) -> int:
  level = level.lower()
  if level == "critical": return 50
  if level == "error": return 40
  if level == "warning": return 30
  if level == "info": return 20
  if level == "debug": return 10