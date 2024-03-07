# REST-API Project (Restuarant management)
# Run these commands to make a python virtual environment for the project's dependencies:
* $ pipenv shell
* $ pipenv install 
* $ python manage.py runserver

**API endpoints**

This document describes all the required API routes for the food delivery app project. The endpoints are grouped into several categories:

* User registration and token generation endpoints
* Menu-items endpoints
* User group management endpoints
* Cart management endpoints
* Order management endpoints

**User registration and token generation endpoints**

These endpoints are used to register new users and generate access tokens.

* `/api/users`
* `/api/users/users/me/`
* `/token/login/`

**Menu-items endpoints**

These endpoints are used to manage menu items.

* `/api/menu-items`
* `/api/menu-items/{menuItem}`

**User group management endpoints**

These endpoints are used to manage user groups.

* `/api/groups/manager/users`
* `/api/groups/manager/users/{userId}`
* `/api/groups/delivery-crew/users`
* `/api/groups/delivery-crew/users/{userId}`

**Cart management endpoints**

These endpoints are used to manage the cart.

* `/api/cart/menu-items`

**Order management endpoints**

These endpoints are used to manage orders.

* `/api/orders`
* `/api/orders/{orderId}`

**HTTP status codes**

The API returns the following HTTP status codes:

* `200 OK`
* `400 Bad Request`
* `401 Unauthorized`
* `403 Forbidden`
* `404 Not Found`
* `500 Internal Server Error`

**Example requests and responses**

The following are examples of requests and responses for some of the API endpoints:

* **Request to register a new user:**

```
POST /api/users

{
  "username": "johndoe",
  "email": "johndoe@example.com",
  "password": "password"
}
```

* **Response to register a new user:**

```
HTTP/1.1 201 Created

{
  "id": 1,
  "username": "johndoe",
}
```
* **Response to login:**
  ```
  POST `/token/login/`
  
  HTTP/1.1 200 OK
   {
     "token":"generated-oken-to-use-when-sending-requests"
   }
  ```

* **Request to get all menu items:**

```
GET /api/menu-items
```

* **Response to get all menu items:**

```
HTTP/1.1 200 OK

{
  "menuItems": [
    {
      "id": 1,
      "name": "Pizza",
      "price": 10.00,
      "category": "Italian"
    },
    {
      "id": 2,
      "name": "shawarma",
      "price": 5.00,
      "category": "Middle eastern"
    },
    {
      "id": 3,
      "name": "Burger",
      "price": 7.00,
      "category": "Western"
    }
  ]
}
```

