from __future__ import annotations

import hashlib
import hmac
import logging
import os
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

logger = logging.getLogger("tradebot.client")

BASE_URL = "https://testnet.binancefuture.com"
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3


class BinanceAPIError(Exception):
    def __init__(self, statusCode: int, code: int, message: str):
        self.statusCode = statusCode
        self.code = code
        self.message = message
        super().__init__(
            f"Binance API Error [{statusCode}]  code={code}  msg={message}"
        )


class BinanceClient:
    def __init__(
        self,
        apiKey: Optional[str] = None,
        apiSecret: Optional[str] = None,
    ):
        logger.debug("Loading environment variables from .env file")
        load_dotenv()

        self.apiKey = apiKey or os.getenv("BINANCE_TESTNET_API_KEY", "")
        self.apiSecret = apiSecret or os.getenv("BINANCE_TESTNET_API_SECRET", "")

        if not self.apiKey or not self.apiSecret:
            logger.error("API credentials not found in environment or .env file")
            raise EnvironmentError(
                "Binance API credentials not found. "
                "Set BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET "
                "in a .env file or as environment variables."
            )

        logger.debug("API key loaded: %s...%s", self.apiKey[:4], self.apiKey[-4:])
        logger.debug("API secret loaded: %s...%s", self.apiSecret[:4], self.apiSecret[-4:])

        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.apiKey,
            "Content-Type": "application/x-www-form-urlencoded",
        })
        logger.debug("HTTP session created with API key header")
        logger.info("BinanceClient initialised — base URL: %s", BASE_URL)

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params["timestamp"] = int(time.time() * 1000)
        logger.debug("Added timestamp to params: %s", params["timestamp"])
        queryString = urlencode(params)
        logger.debug("Query string for signing: %s", queryString)
        signature = hmac.new(
            self.apiSecret.encode("utf-8"),
            queryString.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        logger.debug("Generated HMAC-SHA256 signature: %s...%s", signature[:8], signature[-8:])
        return params

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        params = dict(params or {})
        logger.info("Preparing %s request to %s", method, path)
        logger.debug("Raw params before signing: %s", params)

        if signed:
            logger.debug("Request requires signing — generating signature")
            params = self._sign(params)

        url = BASE_URL + path
        logger.info(">>> Sending %s %s", method, url)
        logger.debug(">>> Full params: %s", params)

        lastExc: Optional[Exception] = None
        for attempt in range(1, MAX_RETRIES + 1):
            logger.debug("Attempt %d/%d", attempt, MAX_RETRIES)
            try:
                resp = self.session.request(
                    method,
                    url,
                    params=params if method == "GET" else None,
                    data=urlencode(params) if method == "POST" else None,
                    timeout=REQUEST_TIMEOUT,
                )
                logger.debug("Request succeeded on attempt %d", attempt)
                break
            except requests.exceptions.ConnectionError as exc:
                lastExc = exc
                logger.warning(
                    "Connection error on attempt %d/%d: %s",
                    attempt, MAX_RETRIES, exc,
                )
                if attempt < MAX_RETRIES:
                    sleepTime = 1 * attempt
                    logger.debug("Sleeping %ds before retry", sleepTime)
                    time.sleep(sleepTime)
            except requests.exceptions.Timeout as exc:
                lastExc = exc
                logger.warning(
                    "Timeout on attempt %d/%d (timeout=%ds): %s",
                    attempt, MAX_RETRIES, REQUEST_TIMEOUT, exc,
                )
                if attempt < MAX_RETRIES:
                    sleepTime = 1 * attempt
                    logger.debug("Sleeping %ds before retry", sleepTime)
                    time.sleep(sleepTime)
        else:
            logger.error("All %d request attempts failed — giving up", MAX_RETRIES)
            raise lastExc

        logger.info("<<< Response status: %d", resp.status_code)
        logger.debug("<<< Response headers: %s", dict(resp.headers))
        logger.debug("<<< Response body: %s", resp.text[:1000])

        try:
            data = resp.json()
            logger.debug("Response parsed as JSON successfully")
        except ValueError:
            logger.error("Failed to parse response as JSON: %s", resp.text[:500])
            resp.raise_for_status()
            return {}

        if resp.status_code >= 400 or (isinstance(data, dict) and "code" in data and data["code"] < 0):
            code = data.get("code", resp.status_code)
            msg = data.get("msg", resp.text[:200])
            logger.error("Binance API returned error — HTTP %d, code=%s, msg=%s", resp.status_code, code, msg)
            raise BinanceAPIError(resp.status_code, code, msg)

        logger.debug("Request completed successfully")
        return data

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        logger.debug("GET %s (signed=%s)", path, signed)
        return self._request("GET", path, params, signed)

    def post(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = True,
    ) -> Dict[str, Any]:
        logger.debug("POST %s (signed=%s)", path, signed)
        return self._request("POST", path, params, signed)
