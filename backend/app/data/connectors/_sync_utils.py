import asyncio
import concurrent.futures

def run_async_safely(coro):
    """
    Run async coro safely even if event loop is already running (e.g., in TestClient).
    Uses thread pool fallback to avoid access violation on Windows.
    """
    def _run():
        return asyncio.run(coro)
    try:
        return asyncio.run(coro)
    except RuntimeError as e:
        msg = str(e).lower()
        if "running" in msg or "cannot be called from a running event loop" in msg:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_run)
                return future.result(timeout=15)
        # Fallback new loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
