import google.generativeai as genai
genai.configure(api_key="AIzaSyAj_3lzrAgbc3dNAdhQiUWXiWD_SiIOZ4Y")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)