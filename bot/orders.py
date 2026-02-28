from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from bot.client import BinanceClient
from bot.validators import (
    validateOrderType,
    validatePrice,
    validateQuantity,
    validateSide,
    validateSymbol,
)

logger = logging.getLogger("tradebot.orders")

ORDER_ENDPOINT = "/fapi/v1/order"


def placeOrder(
    client: BinanceClient,
    symbol: str,
    side: str,
    orderType: str,
    quantity: float,
    price: Optional[float] = None,
) -> Dict[str, Any]:
    logger.info("=== Starting order placement ===")
    logger.debug("Raw inputs — symbol=%s, side=%s, orderType=%s, quantity=%s, price=%s",
                 symbol, side, orderType, quantity, price)

    logger.info("Running input validation")
    symbol = validateSymbol(symbol)
    side = validateSide(side)
    orderType = validateOrderType(orderType)
    quantity = validateQuantity(quantity)
    price = validatePrice(price, orderType)
    logger.info("All inputs validated successfully")

    params: Dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "type": orderType,
        "quantity": quantity,
    }

    if orderType == "LIMIT":
        params["price"] = price
        params["timeInForce"] = "GTC"
        logger.debug("LIMIT order — added price=%s and timeInForce=GTC", price)

    logger.info(
        "Placing %s %s order: symbol=%s  qty=%s  price=%s",
        side, orderType, symbol, quantity, price,
    )
    logger.debug("Final API params: %s", params)

    logger.info("Sending order to Binance API endpoint: %s", ORDER_ENDPOINT)
    response = client.post(ORDER_ENDPOINT, params=params, signed=True)

    logger.info("Order placed — orderId=%s, status=%s",
                response.get("orderId", "N/A"), response.get("status", "N/A"))
    logger.debug("Full order response: %s", response)
    logger.info("=== Order placement complete ===")
    return response


def formatOrderRequest(
    symbol: str,
    side: str,
    orderType: str,
    quantity: float,
    price: Optional[float],
) -> str:
    logger.debug("Formatting order request summary for display")
    lines = [
        "",
        "┌─────────────────────────────────────────┐",
        "│           ORDER REQUEST SUMMARY          │",
        "├─────────────────────────────────────────┤",
        f"│  Symbol     : {symbol:<25s} │",
        f"│  Side       : {side:<25s} │",
        f"│  Type       : {orderType:<25s} │",
        f"│  Quantity   : {str(quantity):<25s} │",
    ]
    if price is not None:
        lines.append(f"│  Price      : {str(price):<25s} │")
    lines += [
        "└─────────────────────────────────────────┘",
        "",
    ]
    logger.debug("Order request summary formatted")
    return "\n".join(lines)


def formatOrderResponse(resp: Dict[str, Any]) -> str:
    logger.debug("Formatting order response for display")
    orderId = resp.get("orderId", "N/A")
    status = resp.get("status", "N/A")
    executedQty = resp.get("executedQty", "N/A")
    avgPrice = resp.get("avgPrice", "N/A")
    clientOrderId = resp.get("clientOrderId", "N/A")
    orderType = resp.get("type", "N/A")
    side = resp.get("side", "N/A")
    symbol = resp.get("symbol", "N/A")
    origQty = resp.get("origQty", "N/A")
    price = resp.get("price", "N/A")
    timeInForce = resp.get("timeInForce", "N/A")

    logger.debug("Extracted response fields — orderId=%s, status=%s, executedQty=%s, avgPrice=%s",
                 orderId, status, executedQty, avgPrice)

    lines = [
        "",
        "┌─────────────────────────────────────────┐",
        "│          ORDER RESPONSE DETAILS          │",
        "├─────────────────────────────────────────┤",
        f"│  Order ID      : {str(orderId):<22s} │",
        f"│  Client OID    : {str(clientOrderId):<22s} │",
        f"│  Symbol        : {str(symbol):<22s} │",
        f"│  Side          : {str(side):<22s} │",
        f"│  Type          : {str(orderType):<22s} │",
        f"│  Status        : {str(status):<22s} │",
        f"│  Orig Qty      : {str(origQty):<22s} │",
        f"│  Executed Qty  : {str(executedQty):<22s} │",
        f"│  Avg Price     : {str(avgPrice):<22s} │",
        f"│  Price         : {str(price):<22s} │",
        f"│  Time in Force : {str(timeInForce):<22s} │",
        "└─────────────────────────────────────────┘",
        "",
    ]
    logger.debug("Order response formatted for display")
    return "\n".join(lines)
