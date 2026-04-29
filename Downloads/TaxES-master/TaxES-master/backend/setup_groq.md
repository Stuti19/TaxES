# Groq API Setup

## Get Free Groq API Key

1. Visit: https://console.groq.com/
2. Sign up for a free account
3. Go to API Keys section
4. Create a new API key
5. Copy the key (starts with `gsk_`)

## Add to Environment

1. Open `.env` file
2. Replace `gsk_your_groq_api_key_here` with your actual API key:
   ```
   GROQ_API_KEY=gsk_your_actual_api_key_here
   ```

## Test the Parser

Run this command to test:
```bash
python groq_parser.py
```

## Features

The Groq parser will:
- Parse "Anjali" → first_name: "Anjali", middle_name: "", last_name: ""
- Parse address into structured components for Excel form
- Fallback to simple parsing if API fails
- Use free Llama3-8B model (fast and accurate)