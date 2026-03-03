import os
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.tools import ToolRegistry # Senin eski Playwright araçların

# 1. API Bağlantısı (Buraya kendi anahtarını yapıştır dayı)
os.environ["GOOGLE_API_KEY"] = "SENIN_API_ANAHTARIN"

# 2. Süper Beyni Tanımla
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

# 3. ARAÇLARI ÇEK
tools = ToolRegistry()
search_tool = tools.search_and_browse # Senin o meşhur internete sızma aracın

# 4. EKİBİ KURUYORUZ

# ARAŞTIRMACI: İnternetteki ham veriyi söküp getiren "dedektif"
researcher = Agent(
    role='Kıdemli Veri Dedektifi',
    goal='{topic} hakkında internetteki en güncel ve kesin kanıtları bulmak.',
    backstory='Sen asla yalanlara inanmazsın. Veriyi bulur, kaynağını doğrular ve ham halde sunarsın.',
    tools=[search_tool],
    llm=llm,
    verbose=True
)

# ANALİST: Verileri çapraz sorgulayan "yalan savar"
analyst = Agent(
    role='Baş Analiz Uzmanı',
    goal='Araştırmacıdan gelen verilerdeki çelişkileri bulup en doğru sonucu süzmek.',
    backstory='Sen rakamların ve tarihlerin efendisisin. 2026 yılındasın ve eski bilgileri anında elersin.',
    llm=llm,
    verbose=True
)

# AHMET: Dayı'ya samimi dille bilgi veren "ekip lideri"
ahmet = Agent(
    role='Mami Dayı\'nın Sağ Kolu Ahmet',
    goal='Analiz edilen bilgiyi samimi, dürüst ve net bir şekilde Dayı\'ya anlatmak.',
    backstory='Samsunlu, mert, dürüst ve samimi bir asistan. Dayı\'sına asla yalan söylemez.',
    llm=llm,
    verbose=True
)

# 5. GÖREVLERİ TANIMLA
research_task = Task(
    description="{topic} konusunu internette en az 3 farklı kaynaktan araştır ve skor/tarih/fiyat gibi kritik verileri topla.",
    agent=researcher
)

analyze_task = Task(
    description="Toplanan verileri karşılaştır. Çelişki varsa internete geri dönüp teyit et. Kesin sonucu belirle.",
    agent=analyst
)

reporting_task = Task(
    description="Doğrulanmış sonucu Mami Dayı'ya samimi bir dille, kısa ve öz olarak raporla.",
    agent=ahmet
)

# 6. OPERASYONU BAŞLAT (CREW)
ahmet_crew = Crew(
    agents=[researcher, analyst, ahmet],
    tasks=[research_task, analyze_task, reporting_task],
    process=Process.sequential # Önce araştır, sonra analiz et, sonra anlat.
)

def sor_bakalim(soru):
    result = ahmet_crew.kickoff(inputs={'topic': soru})
    return result