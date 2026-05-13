# PennyWise — Project Documentation

## 1. Vision

An application for intelligent expense management based on receipt scans. The user uploads a photo of a receipt, and the system automatically extracts data (store name, date, total amount, category) and presents it on a dashboard with charts.

## 2. Tech Stack

| Layer              | Technology                                                              |
|--------------------|-------------------------------------------------------------------------|
| Frontend           | Next.js 14 (App Router), TypeScript, Tailwind CSS, Shadcn/UI, Recharts |
| Backend            | Python 3.12, FastAPI (async)                                            |
| Database           | PostgreSQL                                                              |
| OCR                | EasyOCR                                                                 |
| AI / Parser        | Claude API (claude-haiku-4-5)                                           |
| Auth               | JWT (python-jose)                                                       |
| Containerization   | Docker + Docker Compose                                                 |
| Migrations         | Alembic                                                                 |

## 3. MVP Features

### Frontend
- **Auth** — login and registration screens
- **Upload** — Drag & Drop component for images (JPG/PNG)
- **Processing State** — animated waiting state ("Scanning receipt...")
- **Dashboard** — monthly expense summary, pie chart by category, recent transactions list
- **Edit Form** — manual correction of AI-extracted data

### Backend
- **OCR Engine** — endpoint accepting an image file, processing it into raw text
- **AI Parser** — sends text to Claude API, returns structured JSON: `vendor`, `date`, `total_amount`, `currency`, `category`
- **Database API** — CRUD for expenses linked to a specific user
- **Stats API** — endpoints calculating expense totals for charts

## 4. Technical Goals

- Clean, modular, typed code — Pydantic on the backend
- Automatic API documentation (Swagger / OpenAPI)
- Mobile First responsive design

## 5. Database Schema

## 6. Implementation Order
