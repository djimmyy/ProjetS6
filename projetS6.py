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
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import matplotlib.pyplot as plt
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score


"""
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
"""
#Q15:
data = pd.read_csv("vins_bordeaux_clean.csv", encoding="utf-8")
X = data.drop(columns=["Prix"])
y = data["Prix"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=49)
"""print("X_train: " + str(X_train.shape) + ", y_train: " + str(y_train.shape))
print("X_test: " + str(X_test.shape) + ", y_test: " + str(y_test.shape))"""

#Q16/Q17: LR
model_lr = LinearRegression()
model_lr.fit(X_train, y_train)
y_pred_lr = model_lr.predict(X_test)
r2_lr = r2_score(y_test, y_pred_lr)
"score tres faible sans au nombre de features et des donnees"

"""plt.figure(figsize=(5, 5))
plt.scatter(y_pred_lr, y_test, alpha=0.5, color='blue')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
plt.title("RL = " + str(r2_lr))
plt.grid(True)
plt.show()"""

#Q18:
pipeline_mm = make_pipeline(MinMaxScaler(), LinearRegression())
pipeline_mm.fit(X_train, y_train)
y_pred_mm = pipeline_mm.predict(X_test)
r2_mm = r2_score(y_test, y_pred_mm)


pipeline_std = make_pipeline(StandardScaler(), LinearRegression())
pipeline_std.fit(X_train, y_train)
y_pred_std = pipeline_std.predict(X_test)
r2_std = r2_score(y_test, y_pred_std)
"la meme chose"



print("| Methode              | r²          |")
print("|----------------------|-------------|")
print("| LR                   | " + str(r2_lr) + "  |")
print("| Normalisation + LR   | " + str(r2_mm) + "  |")
print("| Standardisation + LR | " + str(r2_std) + " |")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
axes[0].scatter(y_pred_lr, y_test, alpha=0.5, color='red', s=50)
axes[0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--')
axes[0].set_title("LR : " + str(r2_lr))
axes[0].grid(True)

axes[1].scatter(y_pred_mm, y_test, alpha=0.5, color='green', s=50)
axes[1].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--')
axes[1].set_title("MinMax : " + str(r2_mm))
axes[1].grid(True)

axes[2].scatter(y_pred_std, y_test, alpha=0.5, color='blue', s=50)
axes[2].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--')
axes[2].set_title("standardisation : " + str(r2_std))
axes[2].grid(True)
plt.tight_layout()
plt.show()

# Q19:
print("----------------------------------")
print("prix: Min " + str(y.min()) + " Max " + str(y.max()) )

y_log = np.log(y)
X_train, X_test, y_log_train, y_log_test = train_test_split(X, y_log, test_size=0.25, random_state=49)

print("Log prix: Min " + str(y_log_train.min()) + ", Max " + str(y_log_train.max()) )
"c'est plus centre donc peut etre de meilleur performance"


# Q20: RL sur log
pipeline_log_base = LinearRegression()
pipeline_log_base.fit(X_train, y_log_train)

prix_pred_log_base = pipeline_log_base.predict(X_test)
r2_log_base = r2_score(y_log_test, prix_pred_log_base)

pipeline_log_norm = make_pipeline(MinMaxScaler(), LinearRegression())
pipeline_log_norm.fit(X_train, y_log_train)
prix_pred_log_norm = pipeline_log_norm.predict(X_test)
r2_log_norm = r2_score(y_log_test, prix_pred_log_norm)

pipeline_log_std = make_pipeline(StandardScaler(), LinearRegression())
pipeline_log_std.fit(X_train, y_log_train)
prix_pred_log_std = pipeline_log_std.predict(X_test)
r2_log_std = r2_score(y_log_test, prix_pred_log_std)



print("| Methode              | r²          |")
print("|----------------------|-------------|")
print("| LR                   | " + str(r2_log_base) + "  |")
print("| Normalisation        | " + str(r2_log_norm) + "  |")
print("| Standardisation      | " + str(r2_log_std) + " |")
print(" ")
"de meilleure resultat mais pas suffisant"


best_r2_log = max(r2_log_base, r2_log_norm, r2_log_std)
plt.figure(figsize=(6, 6))
plt.scatter(prix_pred_log_base, y_log_test, alpha=0.6, color='purple', s=50)
plt.plot([y_log_test.min(), y_log_test.max()], [y_log_test.min(), y_log_test.max()], 'k--')
plt.xlabel('Prédictions')
plt.ylabel('Prix')
plt.title("best methode: RL" + str(best_r2_log))
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

#Q21: AD
max_depth = {3, 4, 5}
res_simple,res_norm,res_std = {},{},{}

for depth in max_depth:
    model_dt = DecisionTreeRegressor(max_depth=depth, random_state=49)
    model_dt.fit(X_train, y_log_train)
    res_simple[depth] = r2_score(y_log_test, model_dt.predict(X_test))

    pipeline_norm = make_pipeline(MinMaxScaler(), DecisionTreeRegressor(max_depth=depth, random_state=49))
    pipeline_norm.fit(X_train, y_log_train)
    res_norm[depth] = r2_score(y_log_test, pipeline_norm.predict(X_test))
    
    pipeline_std = make_pipeline(StandardScaler(), DecisionTreeRegressor(max_depth=depth, random_state=49))
    pipeline_std.fit(X_train, y_log_train)
    res_std[depth] = r2_score(y_log_test, pipeline_std.predict(X_test))

"pas de nette amelioration par rapport a la regression lineaire"
print("| Methode                  | r²          |")
print("|--------------------------|-------------|")
for depth in max_depth:
    print("| AD " + str(depth) + ": " + str(res_simple[depth]))
print("|----------------------------------")
    
for depth in max_depth:
    print("| AD " + str(depth) + " + StandardScaler: " + str(res_std[depth]))
print("|----------------------------------")

for depth in max_depth:
    print("| AD " + str(depth) + " + MinMaxScaler: " + str(res_norm[depth]))
print("|----------------------------------")

model3 = KNeighborsRegressor(n_neighbors=4)
model3.fit(X_train, y_log_train)
print("Model KNN 4 Score:", model3.score(X_test, y_log_test))
model32 = make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=4))
model32.fit(X_train, y_log_train)
print("Model KNN 4 (StandardScaler) Score:", model32.score(X_test, y_log_test))

model33 = make_pipeline(MinMaxScaler(), KNeighborsRegressor(n_neighbors=4))
model33.fit(X_train, y_log_train)
print("Model KNN 4 (MinMaxScaler) Score:", model33.score(X_test, y_log_test))
model34 = KNeighborsRegressor(n_neighbors=5)
model34.fit(X_train, y_log_train)
print("Model KNN 5 Score:", model34.score(X_test, y_log_test))
model35 = make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=5))
model35.fit(X_train, y_log_train)
print("Model KNN 5 (StandardScaler) Score:", model35.score(X_test, y_log_test))
model36 = make_pipeline(MinMaxScaler(), KNeighborsRegressor(n_neighbors=5))
model36.fit(X_train, y_log_train)

print("Model KNN 5 (MinMaxScaler) Score:", model36.score(X_test, y_log_test))

import seaborn as sns
corr = data.corr()
plt.figure(figsize=(16, 16))
sns.heatmap(corr, annot=True)
plt.title("Matrice de Corrélation", pad=20)
plt.show()