# E-commerce API Documentation

## Overview
This project is an E-commerce API built with FastAPI. It provides endpoints for managing users, products, and shopping carts. The API is designed to be scalable, secure, and easy to use.

## Table of Contents
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Users](#users)
  - [Products](#products)
  - [Shopping Carts](#shopping-carts)
- [Models](#models)
- [Services](#services)

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/ecommerce-api.git
    cd ecommerce-api
    ```

2. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration
Create a `.env` file in the root directory and add the following environment variables:
    ```env
    APP_NAME=E-commerce API
    MONGODB_URI=mongodb://localhost:27017
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    SECRET_KEY=your_secret_key
    ```

## Running the Application
To run the application, use the following command:
    ```bash
    uvicorn main:app --reload
    ```

## Authentication
The API uses OAuth2 with Password (and hashing) as the authentication method. Users need to obtain a token by providing their username and password. The token must be included in the `Authorization` header of requests to protected endpoints.

### Obtaining a Token
To obtain an access token, send a POST request to the `/token` endpoint with the following form data:
- `username`: The user's username
- `password`: The user's password

Example request:
    ```bash
    curl -X POST "http://localhost:8000/token" -H "Content-Type: application/x-www-form-urlencoded" -d "username=user&password=pass"
    ```

The response will include the access token:
    ```json
    {
        "access_token": "your_access_token",
        "token_type": "bearer"
    }
    ```

### Using the Token
Include the token in the `Authorization` header of requests to protected endpoints:
    ```http
    Authorization: Bearer your_access_token
    ```

## API Endpoints

### Users
- `POST /users/`: Create a new user
- `GET /users/{user_id}`: Get user details by ID
- `PUT /users/{user_id}`: Update user details by ID
- `DELETE /users/{user_id}`: Delete user by ID

### Products
- `POST /products/`: Create a new product
- `GET /products/{product_id}`: Get product details by ID
- `PUT /products/{product_id}`: Update product details by ID
- `DELETE /products/{product_id}`: Delete product by ID

### Shopping Carts
- `POST /shopping-carts/`: Create a new shopping cart
- `GET /shopping-carts/{cart_id}`: Get shopping cart details by ID
- `PUT /shopping-carts/{cart_id}`: Update shopping cart details by ID
- `DELETE /shopping-carts/{cart_id}`: Delete shopping cart by ID
- `POST /shopping-carts/{cart_id}/items`: Add item to shopping cart
- `PUT /shopping-carts/{cart_id}/items/{product_id}`: Update item quantity in shopping cart
- `DELETE /shopping-carts/{cart_id}/items/{product_id}`: Remove item from shopping cart
- `DELETE /shopping-carts/{cart_id}/clear`: Clear all items from shopping cart

## Models
### User
- `id: PyObjectId`
- `username: str`
- `email: str`
- `hashed_password: str`

### Product
- `id: PyObjectId`
- `name: str`
- `description: str`
- `price: float`
- `quantity: int`

### ShoppingCart
- `id: PyObjectId`
- `user_id: PyObjectId`
- `items: List[CartItem]`

### CartItem
- `product_id: PyObjectId`
- `quantity: int`

## Services
### UserService
Provides methods for user authentication and management.

### ProductService
Provides methods for product management.

### ShoppingCartService
Provides methods for shopping cart management, including adding, updating, and removing items.

## Scaling and Traffic Handling

To ensure that our E-commerce API can handle increased traffic and scale effectively, we will need implement several strategies and best practices:

### 1. Database Optimization
- **Sharding**: For very large datasets, we can implement sharding to distribute data across multiple servers, improving read and write performance.

### 2. Caching
- **In-Memory Caching**: We will need to use in-memory caching solutions like Redis to store frequently accessed data, reducing the load on the database and improving response times.
- **HTTP Caching**: We can implement HTTP caching headers to allow clients to cache responses, reducing the number of requests to the server.

### 3. Load Balancing
- **Horizontal Scaling**: We deploy multiple instances of our API behind a load balancer to distribute incoming traffic evenly across all instances.
- **Auto-Scaling**: We configure auto-scaling policies to automatically add or remove instances based on traffic patterns and server load.

### 4. Rate Limiting
- **API Rate Limiting**: We will implement rate limiting to prevent abuse and ensure fair usage of our API. This will help in protecting our servers from being overwhelmed by too many requests from a single client.

### 5. Monitoring and Logging
- **Real-Time Monitoring**: We will use monitoring tools like Prometheus and Grafana to track the performance and health of our API in real-time.
- **Centralized Logging**: We can aggregate logs from all instances into a centralized logging system like ELK Stack (Elasticsearch, Logstash, Kibana) for easier analysis and troubleshooting.

### 6. Containerization and Orchestration
- **Docker**: We will need to containerize our application using Docker, ensuring consistency across different environments and simplifying the deployment process.
- **Kubernetes**: We will use Kubernetes for container orchestration, allowing us to manage, scale, and deploy our containerized applications efficiently. Kubernetes provides features like automatic scaling, load balancing, and self-healing, which are essential for handling increased traffic and ensuring high availability.
- **CI/CD Pipeline**: We will implement a CI/CD pipeline using tools like Jenkins or GitHub Actions to automate the build, test, and deployment process. This ensures that new features and bug fixes are deployed quickly and reliably.

By implementing these strategies, we ensure that our E-commerce API can handle increased traffic, scale effectively, and provide a reliable and responsive experience to our users.