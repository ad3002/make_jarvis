from helpers import time_it

@time_it
def get_answer_from_llm(client, text, st_memory=None, lt_memory=None):

    messages = [
            {"role": "system", "content": "Твое имя Милый, ты рад помочь мне и просто поболтать ни о чем, твои реплики короткие, но с юмором."},
        ]
    if lt_memory:
        for m in lt_memory:
            messages.append(
                {"role": "system", "content": "Факты о предыдущем разговоре: " + m["content"]},
            )
    if st_memory:
        for role, message in st_memory:
            messages.append(
                {"role": role, "content": message},
            )
    messages.append(
        {"role": "user", "content": text},
    )

    response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    )
    text = response.choices[0].message.content
    return text

@time_it
def get_random_ice_break(client, st_memory=None, lt_memory=None):

    messages = [
            {"role": "system", "content": "Твое имя Милый, ты радо помочь мне и просто поболтать ни о чем, твои реплики короткие, но с юмором."},
        ]
    if lt_memory:
        for m in lt_memory:
            messages.append(
                {"role": "system", "content": "Факты о предыдущем разговоре: " + m["content"]},
            )
    if st_memory:
        for role, message in st_memory:
            messages.append(
                {"role": role, "content": message},
            )
    messages.append(
        {"role": "user", "content": "Скажи что-нибудь, чтобы прервать затянувшееся молчание"},
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    text = response.choices[0].message.content
    return text