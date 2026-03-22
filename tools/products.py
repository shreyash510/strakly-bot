from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_products(search: str = None, category_id: int = None) -> dict:
    """Get products in the gym's retail inventory.

    Args:
        search: Search by product name (optional)
        category_id: Filter by category ID (optional)

    Use this tool when user asks about:
    - Products available
    - Inventory list
    - What items are for sale
    - Supplements or merchandise
    """
    client = get_api_client()
    try:
        params = {"limit": 50}
        if search:
            params["search"] = search
        if category_id:
            params["categoryId"] = category_id

        response = await client.get("/products", params)
        products = extract_list(response)

        if not products:
            return {"count": 0, "products": [], "message": "No products found."}

        return {
            "count": len(products),
            "products": [
                {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "sku": p.get("sku"),
                    "price": p.get("price"),
                    "stockQuantity": p.get("stockQuantity"),
                    "lowStockThreshold": p.get("lowStockThreshold"),
                    "categoryName": p.get("categoryName"),
                    "isActive": p.get("isActive"),
                }
                for p in products
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_low_stock_products() -> dict:
    """Get products that are running low on stock.

    Use this tool when user asks about:
    - Low stock items
    - Products running out
    - Inventory alerts
    - What needs to be restocked
    """
    client = get_api_client()
    try:
        response = await client.get("/products/low-stock")
        products = extract_list(response)

        if not products:
            return {"count": 0, "products": [], "message": "No low stock products. All stock levels are healthy."}

        return {
            "count": len(products),
            "products": [
                {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "stockQuantity": p.get("stockQuantity"),
                    "lowStockThreshold": p.get("lowStockThreshold"),
                }
                for p in products
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_sales_stats(date_from: str = None, date_to: str = None) -> dict:
    """Get product sales statistics.

    Args:
        date_from: Start date in YYYY-MM-DD format (optional)
        date_to: End date in YYYY-MM-DD format (optional)

    Use this tool when user asks about:
    - Sales statistics
    - Revenue from products
    - How much was sold
    - Product sales report
    """
    client = get_api_client()
    try:
        params = {}
        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to

        response = await client.get("/products/sales/stats", params)
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def void_product_sale(sale_id: int) -> str:
    """Void/delete a single product sale. This restores stock and voids the payment.
    Only admins can void sales.

    Use when: admin wants to void/delete/cancel a product sale, undo a sale, or reverse a transaction.

    Args:
        sale_id: The ID of the product sale to void
    """
    client = get_api_client()
    return await client.delete(f"/products/sales/{sale_id}")


@tool
async def void_batch_sale(payment_id: int) -> str:
    """Void/delete all product sales in a batch (all items purchased together in one transaction).
    This restores stock for all items and voids the payment. Only admins can void sales.

    Use when: admin wants to void an entire batch/transaction of product sales.

    Args:
        payment_id: The payment ID linking all sales in the batch
    """
    client = get_api_client()
    return await client.delete(f"/products/sales/batch/{payment_id}")


@tool
async def get_product_sales(start_date: str = "", end_date: str = "", page: int = 1, limit: int = 15) -> str:
    """Get product sales history with optional date filtering.

    Use when: user asks about sales history, recent sales, sales report, what was sold.

    Args:
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        page: Page number for pagination (default 1)
        limit: Items per page (default 15)
    """
    client = get_api_client()
    params = {"page": page, "limit": limit}
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date
    return await client.get("/products/sales", params)
