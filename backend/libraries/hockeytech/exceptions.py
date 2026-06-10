from typing import Optional


class HockeyTechAPIException(Exception):
    """Base exception class for the HockeyTech API"""

    def __init__(self, message: Optional[str] = None, *args, **kwargs):
        self.message = message
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.message or ""


__all__ = ("HockeyTechAPIException",)
