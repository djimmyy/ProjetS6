from bs4 import BeautifulSoup
from selenium import webdriver
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import pandas as pd
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")



driver = webdriver.Chrome()

def getsoup(url):
  
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-rbf='followed']"))
    )
    return BeautifulSoup(driver.page_source, "html.parser")

def getsoup_produit(url):
    driver.get(url)

    # attendre que les notes critics soient chargées
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div[data-rbf='wine-critic-slide']")
        )
    )

    return BeautifulSoup(driver.page_source, "html.parser")

def liens_vins(soup):
    liens = []
    for a in soup.find_all("a", attrs={"data-rbf": "followed"}):
        href = a.get("href")
        if not href:
            continue
        if not re.search(r"-\d{4}\.html$", href):
            continue
        liens.append("https://www.millesima.fr" + href)
    return list(set(liens))

def prix(soup):
    bloc = soup.find("div", class_=re.compile("ProductPrice_below-price-bloc")) 
    if bloc:
        texte = bloc.get_text()
        texte = texte.split("€")[0].strip()
        return texte.replace(",", ".")
    return "None"
    
def appelation(soup):
    table = soup.find("table")
    if table:
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) > 1 and cols[0].get_text() == "Appellation":
                return cols[1].get_text()
    return "None"

def fact(st):
      st = st.replace("+", "")
      st = st.split("/")[0]
      if "-" in st:
             try:
                a, b = st.split("-")
                st = str((float(a) + float(b)) / 2) 
             except: pass
      return st

def critic(soup, name):
    critics = soup.find_all("div", {"data-rbf": "wine-critic-slide"})
    for c in critics:
        critic_name = c.find("span", class_=re.compile("WineCriticSlide_name"))
        if critic_name and name.lower() in critic_name.text.lower():
            rating = c.find("span", class_=re.compile("WineCriticSlide_rating"))
            if rating:
                return fact(rating.text)
    return None

def parker(soup):
    return critic (soup, "Parker")
def suckling(soup):
    return critic (soup, "Suckling")
def robinson(soup):
    return critic (soup, "Robinson")

def informations(soup):
    return ",".join([
        str(appelation(soup)),
        str(parker(soup)),
        str(robinson(soup)),
        str(suckling(soup)),
        str(prix(soup))
    ])

def scrape_bordeaux():
    page = 1
    with open("vins_bordeaux.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Appellation","Robert","Robinson","Suckling","Prix"])

        while True:
            url = f"https://www.millesima.fr/bordeaux.html?page={page}"
            print("Page :", page)

            try:
                soup = getsoup(url)
                vins = liens_vins(soup)
                print("Nombre de vins trouvés :", len(vins))

                if not vins:
                    break

                for vin_url in vins:
                    try:
                    
                        vin_soup = getsoup_produit(vin_url)

                        ligne = informations(vin_soup)
                        writer.writerow(ligne.split(","))
                    

                    except Exception as e:
                        print("Erreur vin :", vin_url, e)

                page += 1
            except Exception as e:
                print("Erreur page:", e)
                break

driver.quit()

vins = pd.read_csv("vins_bordeaux.csv", encoding="utf-8")
print(vins.head())
print("--------------------------------------------")
print(vins.info())
print("--------------------------------------------")
print(vins.describe())
print("--------------------------------------------")
#pas sur que ce soit utile car qd on scrape je crois on prend que les vins qui ont une appellation, mais a voirs
vins = vins.dropna(subset=["Appellation"])
print(len(vins))
#vins.to_csv("vins_bordeaux_clean.csv",encoding="utf-8")

def to_ascii(chaine):
    if isinstance(chaine, str):
        return chaine.encode("ascii", "ignore").decode("ascii")
    return chaine

vins["Prix"] = vins["Prix"].apply(to_ascii)
vins["Robert"] = vins["Robert"].apply(to_ascii)
vins["Robinson"] = vins["Robinson"].apply(to_ascii)
vins["Suckling"] = vins["Suckling"].apply(to_ascii)
print("--------------------------------------------")
print(vins.info())
print("--------------------------------------------")
print(len(vins))
#vins.to_csv("vins_bordeaux_clean_prix.csv",encoding="utf-8")
print("--------------------------------------------")
print(vins.head())

def average_notes_appellation(avg, colonne):
    avg[colonne] = pd.to_numeric(avg[colonne], errors="coerce")
    resultat = avg.groupby("Appellation")[colonne].mean().fillna(0).reset_index()
    return resultat

avg_Ro = average_notes_appellation(vins, "Robert")
avg_Rob = average_notes_appellation(vins, "Robinson")
avg_Su = average_notes_appellation(vins, "Suckling")
print("-------------------------------------------")
print(avg_Ro.head())
print("-------------------------------------------")
print(avg_Rob.head())
print("-------------------------------------------")
print(avg_Su.head())
