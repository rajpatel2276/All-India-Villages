# 🌍 All India Village Finder

A high-performance search engine designed to navigate the geographical hierarchy of India. This project allows users to search for any village and instantly retrieve its corresponding sub-district, district, and state.

**Live Demo:** https://all-india-villages-zzkq.vercel.app/

---

## 🚀 The Mission
The goal was to build a seamless search experience that handles large-scale geographical data with minimal latency. I focused on a first-principles approach, mastering the logical flow of data from the database to the UI.

## 🛠️ Technical Stack
* **Frontend:** React.js with Vite
* **Backend:** Node.js & Express.js
* **Database:** PostgreSQL (Neon DB)
* **ORM:** Prisma
* **Deployment:** Vercel (Monorepo Configuration)

## 🏗️ Architecture & Features

### 1. Unified Monorepo Routing
I configured a unified `vercel.json` to handle both the API and the Frontend under a single production domain. This eliminated CORS issues and simplified the networking layer.

### 2. Intelligent Search Logic
* **Case-Insensitive Querying:** Implemented via Prisma to ensure user typos don't break the search experience.
* **Relational Mapping:** The backend performs joins across sub-districts, districts, and states tables to provide a full geographical breadcrumb.

### 3. Production Optimizations
* **Singleton Prisma Pattern:** Optimized database connections to prevent exhaustion during Serverless execution.
* **Efficient API Design:** Built to handle real-time input with a lightweight JSON response.

## 💻 Local Setup

1. **Clone the repo:**
   git clone https://github.com/rajpatel2276/All-India-Villages.git

2. **Backend Configuration:**
   Create a `.env` file in the root:
   DATABASE_URL="your_postgresql_url"

3. **Install & Generate:**
   npm install
   npx prisma generate

4. **Frontend Configuration:**
   Create a `.env` in the frontend folder:
   VITE_API_URL="http://localhost:3000"

5. **Run:**
   # Terminal 1 (Root)
   node server.js
   
   # Terminal 2 (Frontend)
   npm run dev

## 🧠 Key Challenges Overcome
* **CORS & Redirects:** Solved 308 Permanent Redirect and CORS policy blocks by aligning environment variables and Express middleware.
* **Serverless Database Connections:** Managed PostgreSQL connection pooling to ensure stability on Vercel's edge network.

## 👤 Author
**Raj Patel**
Computer Science & Engineering Student
Independent Machine Learning Researcher
