-- Create database
CREATE DATABASE portfolio_db WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'English_India.1252';

-- Create schema
CREATE SCHEMA public;

-- Users table
CREATE TABLE public.users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trades table
CREATE TABLE public.trades (
    id INTEGER PRIMARY KEY,
    stock_name VARCHAR(100),
    entry_date DATE,
    entry_note TEXT,
    exit_date DATE,
    journal TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL REFERENCES public.users(id),
    status VARCHAR(10) DEFAULT 'Open' NOT NULL
);

-- Trade Entries
CREATE TABLE public.trade_entries (
    id INTEGER PRIMARY KEY,
    trade_id INTEGER REFERENCES public.trades(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    date DATE NOT NULL,
    note TEXT,
    invested_amount NUMERIC(10,2) GENERATED ALWAYS AS (quantity * price) STORED
);

-- Trade Exits
CREATE TABLE public.trade_exits (
    id INTEGER PRIMARY KEY,
    trade_id INTEGER REFERENCES public.trades(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    date DATE NOT NULL,
    note TEXT,
    exit_amount NUMERIC(10,2) GENERATED ALWAYS AS (quantity * price) STORED
);

-- Day Notes
CREATE TABLE public.day_notes (
    id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    summary VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE
);

-- Note Images
CREATE TABLE public.note_images (
    id INTEGER PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    note_id INTEGER REFERENCES public.day_notes(id) ON DELETE CASCADE
);

-- Resources
CREATE TABLE public.resources (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    category VARCHAR(20),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags VARCHAR(100),
    pinned BOOLEAN DEFAULT false,
    last_accessed TIMESTAMP,
    user_id INTEGER REFERENCES public.users(id)
);

-- Watchlist
CREATE TABLE public.watchlist (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    stock_name VARCHAR(50) NOT NULL,
    target_price NUMERIC(10,2) NOT NULL CHECK (target_price > 0),
    stop_loss NUMERIC(10,2) NOT NULL CHECK (stop_loss > 0),
    expected_move NUMERIC(10,2) NOT NULL CHECK (expected_move > 0),
    setup_type VARCHAR(30) NOT NULL,
    confidence VARCHAR(10),
    date_added DATE DEFAULT CURRENT_DATE NOT NULL,
    notes TEXT,
    status VARCHAR(20) DEFAULT 'Open' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
