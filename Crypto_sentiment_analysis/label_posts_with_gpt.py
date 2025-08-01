import json
import pandas as pd
from openai import OpenAI

# === CONFIG ===
INPUT_JSON = "bitcointalk_posts.json"
OUTPUT_CSV = "bitcointalk_posts_labeled_gpt.csv"
OPENAI_API_KEY = "sk-..."  # set your key here
MODEL = "gpt-4o-mini"
client = OpenAI(api_key=OPENAI_API_KEY)

# === Load Posts ===
with open(INPUT_JSON, "r") as f:
    posts = json.load(f)

print(f"Loaded {len(posts)} posts")

# === Prompt Template ===
def create_prompt(message):
    return f"""You're analyzing a Bitcoin forum post. 
If the post contains a Bitcoin deposit address (e.g., to receive payment or donation), label it as "Contains address".
If it discusses payment, donation, or sending BTC without an address, use "Mentions transaction".
For technical topics like mining, blocks, or nodes, use "Mentions bitcoin operation".
For market behavior (price, trading, buying/selling), use "Mentions market behavior".
For governance, polls, or platform opinions, use "Mentions governance or opinion".
If it's a help question, label it "Support or question".
If nothing fits, label it "General discussion".

Post: {message}
Label:"""

# === Label Each Post ===
def get_label_from_gpt(prompt):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=20,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error: {e}")
        return "[API Error]"

# === Run Labeling ===
labeled = []
for i, post in enumerate(posts):
    message = post.get("message", "").strip()
    prompt = create_prompt(message)
    print(f"[{i+1}/{len(posts)}] Sending prompt to GPT...")
    label = get_label_from_gpt(prompt)
    labeled.append({
        "thread_id": post.get("thread_id"),
        "thread_title": post.get("thread_title"),
        "author": post.get("author"),
        "timestamp": post.get("timestamp"),
        "message": message,
        "gpt_label": label
    })

# === Save Results ===
df = pd.DataFrame(labeled)
df.to_csv(OUTPUT_CSV, index=False)
print(f"\nSaved labeled output to {OUTPUT_CSV}")

