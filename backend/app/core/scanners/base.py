from abc import ABC, abstractmethod
from typing import Dict, Optional
import asyncio
import logging

class BaseScanner(ABC):
    """Base class for all VAPT scanners."""

    def __init__(self, scanner_type: str):
        """
        Initialize the base scanner.

        Args:
            scanner_type: Type of scanner (web, api, mobile, etc.)
        """
        self.scanner_type = scanner_type
        self.logger = logging.getLogger(f"vapt.scanner.{scanner_type}")
        self.status = "idle"
        self._current_scan = None

    @abstractmethod
    async def scan(self, target: str, **kwargs) -> Dict:
        """
        Abstract method to perform the scan.

        Args:
            target: The target to scan
            **kwargs: Additional scan parameters

        Returns:
            Dict containing scan results
        """
        pass

    async def start_scan(self, target: str, **kwargs) -> str:
        """
        Start a new scan.

        Args:
            target: The target to scan
            **kwargs: Additional scan parameters

        Returns:
            Scan ID
        """
        if self.status == "running":
            raise RuntimeError("Scanner is already running")

        self.status = "running"
        self._current_scan = asyncio.create_task(self.scan(target, **kwargs))

        return f"{self.scanner_type}_{id(self._current_scan)}"

    async def get_status(self) -> Dict:
        """
        Get current scanner status.

        Returns:
            Dict containing scanner status information
        """
        return {
            "type": self.scanner_type,
            "status": self.status,
            "current_scan": bool(self._current_scan)
        }

    async def stop_scan(self) -> None:
        """Stop the current scan if running."""
        if self._current_scan and not self._current_scan.done():
            self._current_scan.cancel()
            try:
                await self._current_scan
            except asyncio.CancelledError:
                pass
            finally:
                self.status = "idle"
                self._current_scan = None

    def _log_error(self, message: str, error: Optional[Exception] = None) -> None:
        """
        Log an error message.

        Args:
            message: Error message
            error: Optional exception object
        """
        if error:
            self.logger.error(f"{message}: {str(error)}")
        else:
            self.logger.error(message)

    def _log_info(self, message: str) -> None:
        """
        Log an info message.

        Args:
            message: Info message
        """
        self.logger.info(message)
