# 📚 BookVerse  

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)  
![FastAPI](https://img.shields.io/badge/FastAPI-Async-green?logo=fastapi)  
![gRPC](https://img.shields.io/badge/gRPC-ProtoBuf-orange?logo=grpc)  
![Postgres](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)  
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)  
![License](https://img.shields.io/badge/License-MIT-yellow)  

---

BookVerse is a modern backend service for managing books, powered by **gRPC**, **FastAPI**, and **PostgreSQL**.  
It is fully **asynchronous**, **containerized**, and ready to be deployed on **Docker Hub** or cloud platforms.  

---

## 🚀 Features
✅ gRPC-based **BooksService** for scalable communication  
✅ REST API with **FastAPI** (as a gateway)  
✅ Full **CRUD** for book management  
✅ **Async PostgreSQL** with SQLAlchemy  
✅ Containerized with **Docker Compose**  

---

## 🛠️ Tech Stack
- ⚡ **Python 3.12**
- 🛰️ **gRPC + Protocol Buffers**
- 🌐 **FastAPI**
- 🗄️ **PostgreSQL**
- 🐳 **Docker & Docker Compose**

---

## 📦 Setup & Run

```bash
# Clone the repository
git clone https://github.com/your-username/bookverse.git
cd bookverse

# Build and start services with Docker Compose
docker-compose up --build
