from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import argparse
import time
import os

def GetPage(value):
    return (int)(value/100)

def Main():
    parser = argparse.ArgumentParser(description="Un esempio di come passare argomenti da riga di comando")

    parser.add_argument('start', type=int, help='da quale capitolo iniziamo')  # Argomento obbligatorio
    parser.add_argument('end', type=int, help='a quale capitolo arriviamo')  # Argomento obbligatorio
    parser.add_argument('--wait', type=int, default=5, help='intevallo di tempo tra l apertura di un link all altro')

    args = parser.parse_args()

    print(f"Scarico dal capitolo {args.start}")
    print(f" al capitolo {args.end}")
    print(f" con intervallo di tempo: {args.wait}")

    if args.start<1:
        raise Exception("il parametro start deve essere maggiore di 0")
    if args.end<args.start:
        raise Exception("il parametro end deve essere maggiore o uguale a start")
    if args.wait<1:
        raise Exception("il parametr wait deve essere almeno di 1 secondo")
    return args.start, args.end, args.wait

if __name__ == "__main__":
    x,y,intervallo = Main()

if not os.path.exists("Chapters"):
        os.makedirs("Chapters")    

url = "https://www.lightnovelworld.co/novel/versatile-mage-web-novel-05122222/chapters"

options = webdriver.ChromeOptions()
prefs = {
        "profile.default_content_setting_values.cookies": 1,  # 2: Blocca, 1: Consenti, 0: Rilevamento
        "profile.managed_default_content_settings.cookies": 2
    }
options.add_experimental_option("prefs", prefs)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver2 = webdriver.Chrome(service=service, options=options)


startPage = GetPage(x)
endPage = GetPage(y)
nPages = endPage-startPage

print(f"inizio page: {startPage}, fine page: {endPage}, nPages: {nPages}")

for indexPage in range(startPage,endPage+1):
    
    driver.get(os.path.join(url,f"?page={indexPage+1}"))
    WebDriverWait(driver, 30).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
    
    container = driver.find_element(By.CLASS_NAME, "chapter-list")
    chapter_list = container.find_elements(By.TAG_NAME, 'li')

    startRange = (x-1)%100 if GetPage(x)==indexPage else 0 # GetPage(x)==indexPage ? (x-1)%100 : 0
    endRange = (y%100) if GetPage(y) == indexPage else 100 # GetPage(y) == indexPage ? (y%100) : 100
    for i, ch in enumerate(chapter_list[startRange:endRange], start = startRange+1):  #for ch in chapter_list[x-1:y]:
        try:
            print(f"i: {i}, ch: {ch}")
            href_value = ch.find_element(By.TAG_NAME, 'a').get_attribute('href')
            print(href_value)
            driver2.get(href_value)
        
            WebDriverWait(driver2, 30).until(
                lambda driver2: driver2.execute_script("return document.readyState") == "complete"
            )
            chapter_container = driver2.find_element(By.ID, "chapter-container")
            title_ph = driver2.find_element(By.CLASS_NAME,"chapter-title")
            paragraphs = chapter_container.find_elements(By.TAG_NAME, 'p')
            with open(f"Chapters/capitolo_{i+(indexPage*100)}.txt", "w", encoding="utf-8") as file:
                file.write(title_ph.text+"\n\n")
                for paragraph in paragraphs:
                    file.write(paragraph.text + "\n\n")
            time.sleep(intervallo)
        
        except Exception as e:
                print(f"Errore durante l'elaborazione del capitolo: {e}")
                continue

driver.quit()
driver2.quit()
