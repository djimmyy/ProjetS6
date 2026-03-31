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
    
def appellation(soup):
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
        str(appellation(soup)),
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
vins["Prix"] = pd.to_numeric(vins["Prix"], errors="coerce")
vins["Robert"] = vins["Robert"].apply(to_ascii)
vins["Robert"] = pd.to_numeric(vins["Robert"], errors="coerce")
vins["Robinson"] = vins["Robinson"].apply(to_ascii)
vins["Robinson"] = pd.to_numeric(vins["Robinson"], errors="coerce")
vins["Suckling"] = vins["Suckling"].apply(to_ascii)
vins["Suckling"] = pd.to_numeric(vins["Suckling"], errors="coerce")
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

print("-------------------------------------------")
print ("--------------------------------------------")
print(vins.isna().sum())

avg_Ro = avg_Ro.rename(columns={"Robert": "Robert_moy"})
avg_Rob = avg_Rob.rename(columns={"Robinson": "Robinson_moy"})
avg_Su = avg_Su.rename(columns={"Suckling": "Suckling_moy"})

vins = vins.merge(avg_Ro, on="Appellation", how="left")
vins = vins.merge(avg_Rob, on="Appellation", how="left")
vins = vins.merge(avg_Su, on="Appellation", how="left")

vins["Robert"] = vins["Robert"].fillna(vins["Robert_moy"])
vins["Robinson"] = vins["Robinson"].fillna(vins["Robinson_moy"])
vins["Suckling"] = vins["Suckling"].fillna(vins["Suckling_moy"])

vins = vins.drop(columns=["Robert_moy","Robinson_moy","Suckling_moy"])

vins = pd.get_dummies(vins, columns=["Appellation"], prefix="Appellation",dtype=int)
vins = vins.round(2)
vins.to_csv("vins_bordeaux_clean.csv",index=False,encoding="utf-8")

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler

X = vins.drop(columns=["Prix"])
y = vins["Prix"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=49)

model3 = KNeighborsRegressor(n_neighbors=4)
model3.fit(X_train, y_train)

print("Model KNN 4 Score:", model3.score(X_test, y_test))

model32 = make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=4))
model32.fit(X_train, y_train)
print("Model KNN 4 (StandardScaler) Score:", model32.score(X_test, y_test))

model33 = make_pipeline(MinMaxScaler(), KNeighborsRegressor(n_neighbors=4))
model33.fit(X_train, y_train)
print("Model KNN 4 (MinMaxScaler) Score:", model33.score(X_test, y_test))
# en faisant le pretraitement il y a une legere amelioration du score, mais pas significative, les scores obtenus ne sont pas satisfaisants.
model34 = KNeighborsRegressor(n_neighbors=5)
model34.fit(X_train, y_train)
print("Model KNN 5 Score:", model34.score(X_test, y_test))
model35 = make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=5))
model35.fit(X_train, y_train)
print("Model KNN 5 (StandardScaler) Score:", model35.score(X_test, y_test))
model36 = make_pipeline(MinMaxScaler(), KNeighborsRegressor(n_neighbors=5))
model36.fit(X_train, y_train)
print("Model KNN 5 (MinMaxScaler) Score:", model36.score(X_test, y_test))
#l'amelioration n'est pas significative, les scores obtenus ne sont pas satisfaisants, le score est meme pire avec le standard scaler,