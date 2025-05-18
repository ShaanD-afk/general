# BhashaCode

**Live site:** [https://eduai.ranjithrd.in](https://eduai.ranjithrd.in)

## Getting Started

### 1. Clone the repository

```sh
git clone https://github.com/ShaanD-afk/general.git
cd eduai
```

---

## Server (Flask API)

### 2. Environment & Config

-   Copy the provided `.env` file into `server/.env` and fill in the required variables:

```
DB_URL=...
SECRET_KEY=...
CHATGPT_API_KEY=...
AZURE_SPEECH_KEY=...
AZURE_REGION=...
JUDGE_URL=...
```

-   Place your `yoyo.ini` file for database migrations in the `server` folder.

### 3. Install dependencies

```sh
cd server
pip install -r requirements.txt
```

### 4. Run the Flask app

```sh
python main.py
```

---

## Client (Vite + React)

### 5. Install dependencies

```sh
cd ../client
npm install
```

### 6. Build and serve

```sh
npm run build
npm run serve
```

-   The Vite app will be served at [http://localhost:5052](http://localhost:5052) by default.

---

## Notes

-   Make sure your database is set up and migrations are applied using `yoyo` and your `yoyo.ini` config.
-   The Flask server uses the environment variables from `.env` for all secrets and API keys.
-   The client and server can be run independently for development.

---
