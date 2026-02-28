from __future__ import annotations

import logging

logger = logging.getLogger("tradebot.validators")

VALID_SIDES = ("BUY", "SELL")
VALID_ORDER_TYPES = ("MARKET", "LIMIT")


def validateSymbol(symbol: str) -> str:
    logger.debug("Validating symbol: '%s'", symbol)
    if not symbol or not isinstance(symbol, str):
        logger.error("Symbol validation failed: empty or not a string")
        raise ValueError("Symbol must be a non-empty string.")
    symbol = symbol.strip().upper()
    if not symbol.isalpha():
        logger.error("Symbol validation failed: non-alphabetic characters in '%s'", symbol)
        raise ValueError(f"Symbol must contain only letters, got: '{symbol}'")
    if not symbol.endswith("USDT"):
        logger.error("Symbol validation failed: '%s' does not end with USDT", symbol)
        raise ValueError(
            f"Only USDT-M futures pairs are supported. Symbol must end with 'USDT', got: '{symbol}'"
        )
    if len(symbol) < 5:
        logger.error("Symbol validation failed: '%s' is too short", symbol)
        raise ValueError(f"Symbol too short: '{symbol}'")
    logger.debug("Symbol validated successfully: '%s'", symbol)
    return symbol


def validateSide(side: str) -> str:
    logger.debug("Validating side: '%s'", side)
    if not side or not isinstance(side, str):
        logger.error("Side validation failed: empty or not a string")
        raise ValueError("Side must be a non-empty string.")
    side = side.strip().upper()
    if side not in VALID_SIDES:
        logger.error("Side validation failed: '%s' not in %s", side, VALID_SIDES)
        raise ValueError(f"Side must be one of {VALID_SIDES}, got: '{side}'")
    logger.debug("Side validated successfully: '%s'", side)
    return side


def validateOrderType(orderType: str) -> str:
    logger.debug("Validating order type: '%s'", orderType)
    if not orderType or not isinstance(orderType, str):
        logger.error("Order type validation failed: empty or not a string")
        raise ValueError("Order type must be a non-empty string.")
    orderType = orderType.strip().upper()
    if orderType not in VALID_ORDER_TYPES:
        logger.error("Order type validation failed: '%s' not in %s", orderType, VALID_ORDER_TYPES)
        raise ValueError(
            f"Order type must be one of {VALID_ORDER_TYPES}, got: '{orderType}'"
        )
    logger.debug("Order type validated successfully: '%s'", orderType)
    return orderType


def validateQuantity(quantity: float) -> float:
    logger.debug("Validating quantity: '%s'", quantity)
    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        logger.error("Quantity validation failed: '%s' is not a number", quantity)
        raise ValueError(f"Quantity must be a number, got: '{quantity}'")
    if quantity <= 0:
        logger.error("Quantity validation failed: %s is not positive", quantity)
        raise ValueError(f"Quantity must be positive, got: {quantity}")
    logger.debug("Quantity validated successfully: %s", quantity)
    return quantity


def validatePrice(price: float | None, orderType: str) -> float | None:
    logger.debug("Validating price: '%s' for order type: '%s'", price, orderType)
    if orderType == "LIMIT":
        if price is None:
            logger.error("Price validation failed: price is required for LIMIT orders")
            raise ValueError("Price is required for LIMIT orders.")
        try:
            price = float(price)
        except (TypeError, ValueError):
            logger.error("Price validation failed: '%s' is not a number", price)
            raise ValueError(f"Price must be a number, got: '{price}'")
        if price <= 0:
            logger.error("Price validation failed: %s is not positive", price)
            raise ValueError(f"Price must be positive, got: {price}")
        logger.debug("Price validated successfully: %s", price)
        return price
    logger.debug("Price not required for %s order, skipping", orderType)
    return None
