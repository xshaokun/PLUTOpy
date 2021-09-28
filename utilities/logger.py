import logging
import numpy as np

fmLogger = logging.getLogger("Fermi")
fmLogger.setLevel(logging.INFO)
if not fmLogger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    formatter = logging.Formatter("%(name)-3s: [%(levelname)-9s] %(asctime)s %(message)s")
    
    ch.setFormatter(formatter)
    
    fmLogger.addHandler(ch)

def set_log_level(level):
    """
    Select which minimal logging level should be displayed.
    Parameters
    ----------
    level: int or str
        Possible values by increasing level:
        0 or "notset"
        1 or "all"
        10 or "debug"
        20 or "info"
        30 or "warning"
        40 or "error"
        50 or "critical"
    """
    # this is a user-facing interface to avoid importing from skpy.utilities in user code.

    if isinstance(level, str):
        level = level.upper()

    if level == "ALL":  # non-standard alias
        level = 1
    fmLogger.setLevel(level)
    fmLogger.debug("Set log level to %d", level)
