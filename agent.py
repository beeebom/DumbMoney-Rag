import sqlite3
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(Path(__file__).parent / ".env")

def ask_financial_agent(user_question):
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not set. Add it to your .env file.")
        return

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Check for the cheat sheet file
    if not os.path.exists("promt.txt"):
        print("Error: 'promt.txt' not found in this folder!")
        return
        
    with open("promt.txt", "r") as f:
        system_instructions = f.read()

    print(f"\n[YOUR QUESTION]: {user_question}")
    print("Gemini Agent is translating question to database code...")
    
    # 2. Get the SQL query translation from Gemini
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',  # High-speed, highly accurate model for coding tasks
            contents=user_question,
            config=types.GenerateContentConfig(
                system_instruction=system_instructions,
                temperature=0.0  # Keeps the model deterministic and strict
            )
        )
        
        generated_code = response.text.strip()
        
        # Clean away markdown formatting block wrappers if Gemini includes them
        clean_sql = generated_code.replace("```sqlite", "").replace("```sql", "").replace("```", "").strip()
        
        print(f"[GENERATED SQL CODE]:\n{clean_sql}\n")
        
    except Exception as e:
        print(f"Gemini API Connection Error: {e}")
        return

    # 3. Fire the written query directly at your database file
    conn = sqlite3.connect("financial_intelligence.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute(clean_sql)
        results = cursor.fetchall()
        
        print("============ DATA RETRIEVED ============")
        if len(results) == 0:
            print("No matching records found in your database records.")
        for row in results:
            print(" -> ", row)
        print("========================================")
        
    except Exception as sql_error:
        print(f"Database Error! The written SQL code failed to run.")
        print(f"Error Message: {sql_error}")
        
    finally:
        conn.close()

# --- INTERACTIVE TESTING LOOP ---
if __name__ == "__main__":
    # Test your fresh Gemini setup!
    ask_financial_agent("Tell me about differencee in yearly sales and yeearly profit of abb from 2023 to 2026.")