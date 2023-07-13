# REST-API
API endpoints

This document describes all the required API routes for the food delivery app project. The endpoints are grouped into several categories:

User registration and token generation endpoints
Menu-items endpoints
User group management endpoints
Cart management endpoints
Order management endpoints
User registration and token generation endpoints

These endpoints are used to register new users and generate access tokens.

* /api/users
* /api/users/users/me/
* /token/login/
* Menu-items endpoints

These endpoints are used to manage menu items.

/api/menu-items
/api/menu-items/{menuItem}
User group management endpoints

These endpoints are used to manage user groups.

/api/groups/manager/users
/api/groups/manager/users/{userId}
/api/groups/delivery-crew/users
/api/groups/delivery-crew/users/{userId}
Cart management endpoints

These endpoints are used to manage the cart.

/api/cart/menu-items
Order management endpoints

These endpoints are used to manage orders.

/api/orders
/api/orders/{orderId}
HTTP status codes

The API returns the following HTTP status codes:

200 OK
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
500 Internal Server Error
