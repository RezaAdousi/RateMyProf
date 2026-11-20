import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv() 

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)

joined_text = "Good Bad good at speaking loud He's very good, very fluent and have very knowledge He's very good, very fluent and have very knowledge I like him I hate when he coughs, he was sick I think lol hardly gives good grades hardly gives good grades hard to pass his classes good good not bad not bad"

prompt = f"""
    You are a skilled data analyst AI. Analyze the following student reviews of a professor. Your output must follow this format exactly, using **bullet points** for each section:

    **Positive Points 🙂**
    - Each bullet should describe a positive aspect mentioned by students.
    - Only report what is explicitly stated in the reviews; do NOT add any information not present in the student comments.
    - Phrase it naturally and in a neutral, report-like way.
    - Include approximate counts or percentages if possible, e.g., "About 3 students mentioned..." or "Around 70% of students noted...".
    - Use phrases like "some students", "several students", or "many students" if exact numbers are not available.
    - You may use emojis to make each point visually clear, but keep it professional.

    **Negative Points ⚠️**
    - Each bullet should describe a negative aspect noted by students.
    - Only report what is explicitly stated in the reviews; do NOT add any information not present in the student comments.
    - Phrase it similarly in a neutral way.
    - Include approximate counts or percentages if possible.
    - Use phrases like "some students mentioned", "several students reported", or "a few students noted".
    - Emojis can be used to highlight negative points, but keep it clear and concise.

    **Final Opinion 📝**
    - Write a short objective summary based on student reviews.
    - Only summarize the information that exists in the reviews; do NOT add assumptions or extra details.
    - Include overall strengths and weaknesses based on the comments.
    - Mention if more data is needed for a confident conclusion.
    - Use natural phrasing like "appears to", "some students noted", or "based on comments".
    - Use emojis sparingly to improve readability.

    **Overall Rating ⭐**
    - Based on the student reviews, provide a rating out of 5 stars (e.g., 4/5 ⭐) that reflects the general opinion of students.
    - Clearly indicate that this rating is **estimated by AI** based on the comments.
    - Explain briefly in one line why this rating was chosen.
    - Only use information that is present in the reviews to justify the rating.

    Important rules:
    - Do NOT mention the prompt or explain your process.
    - Do NOT fabricate information; only report what is present in the reviews.
    - Write as if you are an academic reviewer summarizing real student feedback.


    Student Reviews:
    {joined_text}

"""

completion = client.chat.completions.create(
    model="google/gemma-2-2b-it:nebius",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
)

print(completion.choices[0].message.content)