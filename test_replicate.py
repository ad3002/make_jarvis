import replicate

replicate.api_token = "r8_5QO5EJEHz6XqCZ2uXUr4YYEa7Ive53S1DTKvN"

output = replicate.run(
    "lucataco/xtts-v2:684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e",
    input={
        "text": "Hi there, I'm your new voice clone. Try your best to upload quality audio",
        "speaker": "https://replicate.delivery/pbxt/Jt79w0xsT64R1JsiJ0LQRL8UcWspg5J4RFrU6YwEKpOT1ukS/male.wav",
        "language": "en",
        "cleanup_voice": False
    }
)
print(output)