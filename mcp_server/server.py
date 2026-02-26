"""
Freqtrade MCP Server

Exposes the Freqtrade REST API as MCP tools so that AI assistants
can query and control a running Freqtrade bot.

Environment variables (all optional – defaults match the doc examples):
  FREQTRADE_SERVER_URL  – default http://127.0.0.1:8080
  FREQTRADE_USERNAME    – default Freqtrader
  FREQTRADE_PASSWORD    – default SuperSecret1!
"""

from __future__ import annotations

import json
import os
import sys

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Make sure the repo root is on sys.path so we can import the client lib
# that lives at ft_client/freqtrade_client/ft_rest_client.py
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FT_CLIENT_DIR = os.path.join(_REPO_ROOT, "ft_client")
if _FT_CLIENT_DIR not in sys.path:
    sys.path.insert(0, _FT_CLIENT_DIR)

from freqtrade_client.ft_rest_client import FtRestClient  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration from environment
# ---------------------------------------------------------------------------
SERVER_URL = os.environ.get("FREQTRADE_SERVER_URL", "http://127.0.0.1:8080")
USERNAME = os.environ.get("FREQTRADE_USERNAME", "Freqtrader")
PASSWORD = os.environ.get("FREQTRADE_PASSWORD", "SuperSecret1!")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _client() -> FtRestClient:
    """Return a fresh client (cheap – no persistent connection pool needed for MCP)."""
    return FtRestClient(SERVER_URL, USERNAME, PASSWORD)


def _json(obj) -> str:
    """Pretty-print any API response as JSON text."""
    return json.dumps(obj, indent=2, default=str)


# ---------------------------------------------------------------------------
# MCP app
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "Freqtrade",
    instructions="MCP server that wraps the Freqtrade REST API to query and control a running trading bot.",
)


# ── Read-only / informational tools ──────────────────────────────────────────

@mcp.tool()
def ping() -> str:
    """Check if the Freqtrade bot is running and responding."""
    return _json(_client().ping())


@mcp.tool()
def version() -> str:
    """Return the version of the running Freqtrade bot."""
    return _json(_client().version())


@mcp.tool()
def show_config() -> str:
    """Return the relevant parts of the running bot configuration."""
    return _json(_client().show_config())


@mcp.tool()
def status() -> str:
    """List all currently open trades with details."""
    return _json(_client().status())


@mcp.tool()
def count() -> str:
    """Return the number of open trades and the maximum allowed."""
    return _json(_client().count())


@mcp.tool()
def balance() -> str:
    """Return the account balance per currency."""
    return _json(_client().balance())


@mcp.tool()
def profit() -> str:
    """Return a profit/loss summary from closed trades and performance stats."""
    return _json(_client().profit())


@mcp.tool()
def daily(days: int = 7) -> str:
    """Return profit/loss per day for the last N days (default 7)."""
    return _json(_client().daily(days))


@mcp.tool()
def weekly(weeks: int = 4) -> str:
    """Return profit/loss per week for the last N weeks (default 4)."""
    return _json(_client().weekly(weeks))


@mcp.tool()
def monthly(months: int = 3) -> str:
    """Return profit/loss per month for the last N months (default 3)."""
    return _json(_client().monthly(months))


@mcp.tool()
def stats() -> str:
    """Return summary statistics: profit/loss reasons and average holding times."""
    return _json(_client().stats())


@mcp.tool()
def performance() -> str:
    """Return performance of each finished trade grouped by pair."""
    return _json(_client().performance())


@mcp.tool()
def trades(limit: int = 50, offset: int = 0) -> str:
    """Return trade history. Limited to 500 trades per call.

    Args:
        limit: Maximum number of trades to return (max 500).
        offset: Offset for pagination.
    """
    return _json(_client().trades(limit=limit, offset=offset))


@mcp.tool()
def trade(trade_id: int) -> str:
    """Return details of a specific trade by its ID.

    Args:
        trade_id: The numeric trade identifier.
    """
    return _json(_client().trade(trade_id))


@mcp.tool()
def entries(pair: str | None = None) -> str:
    """Return profit statistics grouped by entry tag.

    Args:
        pair: Optional pair filter (e.g. "BTC/USDT"). Omit for all pairs.
    """
    return _json(_client().entries(pair))


@mcp.tool()
def exits(pair: str | None = None) -> str:
    """Return profit statistics grouped by exit reason.

    Args:
        pair: Optional pair filter. Omit for all pairs.
    """
    return _json(_client().exits(pair))


@mcp.tool()
def mix_tags(pair: str | None = None) -> str:
    """Return profit statistics for each entry_tag + exit_reason combination.

    Args:
        pair: Optional pair filter. Omit for all pairs.
    """
    return _json(_client().mix_tags(pair))


@mcp.tool()
def whitelist() -> str:
    """Return the current pair whitelist."""
    return _json(_client().whitelist())


@mcp.tool()
def blacklist(add: str | None = None) -> str:
    """Show the current blacklist, or add a pair to it.

    Args:
        add: A pair to add to the blacklist (e.g. "BNB/BTC"). Omit to just show the current list.
    """
    client = _client()
    if add:
        return _json(client.blacklist(add))
    return _json(client.blacklist())


@mcp.tool()
def locks() -> str:
    """Return the list of currently locked pairs."""
    return _json(_client().locks())


@mcp.tool()
def logs(limit: int = 50) -> str:
    """Return the latest log messages from the bot.

    Args:
        limit: Maximum number of log lines to return.
    """
    return _json(_client().logs(limit))


@mcp.tool()
def strategies() -> str:
    """List available strategies in the strategy directory."""
    return _json(_client().strategies())


@mcp.tool()
def strategy(strategy_name: str) -> str:
    """Return the source code / details of a specific strategy.

    Args:
        strategy_name: The strategy class name.
    """
    return _json(_client().strategy(strategy_name))


@mcp.tool()
def available_pairs(timeframe: str | None = None, stake_currency: str | None = None) -> str:
    """List available backtest data pairs.

    Args:
        timeframe: Filter by timeframe (e.g. "5m").
        stake_currency: Filter by stake currency (e.g. "USDT").
    """
    return _json(_client().available_pairs(timeframe, stake_currency))


@mcp.tool()
def pair_candles(pair: str, timeframe: str, limit: int | None = None) -> str:
    """Return live OHLCV candle data for a pair/timeframe.

    Args:
        pair: The trading pair (e.g. "BTC/USDT").
        timeframe: Candle timeframe (e.g. "5m", "1h").
        limit: Optional limit on number of candles.
    """
    return _json(_client().pair_candles(pair, timeframe, limit))


@mcp.tool()
def sysinfo() -> str:
    """Return system information (CPU, RAM usage) of the bot host."""
    return _json(_client().sysinfo())


@mcp.tool()
def health() -> str:
    """Quick health check – shows the last bot processing loop time."""
    return _json(_client().health())


# ── Action tools (mutating) ─────────────────────────────────────────────────

@mcp.tool()
def start_bot() -> str:
    """Start the trading bot (if it is currently stopped)."""
    return _json(_client().start())


@mcp.tool()
def pause_bot() -> str:
    """Pause the trading bot. Open trades are handled gracefully; no new positions are entered."""
    return _json(_client().stop())  # The REST API maps /stop to pause-like behavior


@mcp.tool()
def stop_bot() -> str:
    """Stop the bot from opening new trades. Existing trades are closed gracefully."""
    return _json(_client().stopbuy())


@mcp.tool()
def reload_config() -> str:
    """Reload the bot configuration file without restarting."""
    return _json(_client().reload_config())


@mcp.tool()
def force_enter(
    pair: str,
    side: str = "long",
    price: float | None = None,
    order_type: str | None = None,
    stake_amount: float | None = None,
    leverage: float | None = None,
    enter_tag: str | None = None,
) -> str:
    """Force-enter a new trade immediately.

    Args:
        pair: The trading pair (e.g. "ETH/USDT").
        side: Trade side – "long" or "short" (default "long").
        price: Optional entry price. Uses market price if omitted.
        order_type: Optional order type – "market" or "limit".
        stake_amount: Optional stake amount as a float.
        leverage: Optional leverage multiplier.
        enter_tag: Optional tag for the entry (default "force_enter").
    """
    return _json(
        _client().forceenter(
            pair,
            side,
            price,
            order_type=order_type,
            stake_amount=stake_amount,
            leverage=leverage,
            enter_tag=enter_tag,
        )
    )


@mcp.tool()
def force_exit(trade_id: int | str, order_type: str | None = None, amount: float | None = None) -> str:
    """Force-exit (sell) a trade immediately, ignoring minimum ROI.

    Args:
        trade_id: The trade ID, or "all" to exit every open trade.
        order_type: Optional – "market" or "limit".
        amount: Optional – partial exit amount. Full exit if omitted.
    """
    return _json(_client().forceexit(trade_id, order_type, amount))


@mcp.tool()
def delete_trade(trade_id: int) -> str:
    """Remove a trade from the database and try to close its open orders.

    Requires manual handling of the asset on the exchange afterwards.

    Args:
        trade_id: The trade ID to delete.
    """
    return _json(_client().delete_trade(trade_id))


@mcp.tool()
def cancel_open_order(trade_id: int) -> str:
    """Cancel the currently open order for a trade.

    Args:
        trade_id: The trade ID whose open order should be cancelled.
    """
    return _json(_client().cancel_open_order(trade_id))


@mcp.tool()
def lock_pair(pair: str, until: str, side: str = "*", reason: str = "") -> str:
    """Lock a pair from trading until a specified datetime.

    Args:
        pair: The pair to lock (e.g. "BTC/USDT").
        until: Lock expiry datetime (format "2024-03-30 16:00:00Z").
        side: Side to lock – "long", "short", or "*" for both (default "*").
        reason: Optional human-readable reason for the lock.
    """
    return _json(_client().lock_add(pair, until, side, reason))


@mcp.tool()
def delete_lock(lock_id: int) -> str:
    """Delete (disable) a pair lock by its ID.

    Args:
        lock_id: The lock ID to remove.
    """
    return _json(_client().delete_lock(lock_id))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
