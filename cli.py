from __future__ import annotations

import sys

import click

from bot.client import BinanceAPIError, BinanceClient
from bot.logging_config import setupLogging
from bot.orders import formatOrderRequest, formatOrderResponse, placeOrder


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--symbol", "-s", required=True, help="Trading pair symbol, e.g. BTCUSDT.")
@click.option("--side", required=True, type=click.Choice(["BUY", "SELL"], case_sensitive=False), help="Order side: BUY or SELL.")
@click.option("--type", "orderType", required=True, type=click.Choice(["MARKET", "LIMIT"], case_sensitive=False), help="Order type: MARKET or LIMIT.")
@click.option("--quantity", "-q", required=True, type=float, help="Order quantity (base asset units).")
@click.option("--price", "-p", default=None, type=float, help="Limit price (required for LIMIT orders).")
def main(
    symbol: str,
    side: str,
    orderType: str,
    quantity: float,
    price: float | None,
) -> None:
    logger = setupLogging()

    logger.info("========================================")
    logger.info("  TRADEBOT CLI SESSION STARTED")
    logger.info("========================================")
    logger.info("CLI arguments received — symbol=%s, side=%s, type=%s, quantity=%s, price=%s",
                symbol, side, orderType, quantity, price)

    side = side.upper()
    orderType = orderType.upper()
    logger.debug("Normalised inputs — side=%s, orderType=%s", side, orderType)

    requestSummary = formatOrderRequest(symbol, side, orderType, quantity, price)
    click.echo(requestSummary)
    logger.info("Order request summary displayed to user")

    try:
        logger.info("Initialising Binance API client")
        client = BinanceClient()
        logger.info("Binance API client ready")

        logger.info("Calling placeOrder()")
        response = placeOrder(
            client=client,
            symbol=symbol,
            side=side,
            orderType=orderType,
            quantity=quantity,
            price=price,
        )

        responseSummary = formatOrderResponse(response)
        click.echo(responseSummary)
        logger.info("Order response displayed to user")

        click.secho("✔  Order placed successfully!", fg="green", bold=True)
        logger.info("ORDER SUCCESS — orderId=%s, status=%s",
                     response.get("orderId", "N/A"), response.get("status", "N/A"))

    except ValueError as exc:
        logger.error("VALIDATION ERROR: %s", exc)
        click.secho(f"\n✘  Validation Error: {exc}", fg="red", bold=True)
        sys.exit(1)

    except EnvironmentError as exc:
        logger.error("CONFIGURATION ERROR: %s", exc)
        click.secho(f"\n✘  Configuration Error: {exc}", fg="red", bold=True)
        sys.exit(1)

    except BinanceAPIError as exc:
        logger.error("BINANCE API ERROR: statusCode=%s, code=%s, msg=%s",
                      exc.statusCode, exc.code, exc.message)
        click.secho(f"\n✘  Binance API Error: {exc}", fg="red", bold=True)
        sys.exit(1)

    except Exception as exc:
        logger.exception("UNEXPECTED ERROR: %s", exc)
        click.secho(f"\n✘  Unexpected Error: {exc}", fg="red", bold=True)
        sys.exit(1)

    finally:
        logger.info("========================================")
        logger.info("  TRADEBOT CLI SESSION ENDED")
        logger.info("========================================")


if __name__ == "__main__":
    main()
