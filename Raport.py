# -*- coding: utf-8 -*-
"""kk197_raport.ipynb

Automatically generated by Colaboratory.

# Projekt zaliczeniowy kursu KoronaScience
###Karolina Kondzielnik
29.03.2020

##Wstęp
Projekt zawiera analizę danych dotyczących zachorowań na SARS-CoV-2 oraz przypadków śmiertelnych na terenie poszczególnych województw Polski. Głównym celem jest utworzenie narzędzia, umożliwiającego przeanalizowanie zachodzących zmian w zaawansowanym stadium oraz po zakończeniu epidemii.

Dane pozyskane zostały z 
https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_Poland 
https://pl.wikipedia.org/wiki/Wojew%C3%B3dztwo#Podzia%C5%82_na_wojew%C3%B3dztwa_od_1999_r.
https://en.wikipedia.org/wiki/Voivodeships_of_Poland 
 i ręcznie umieszczone w plikach csv w repozytorium https://github.com/kk197/KoronaScience_Raport z powodu braku oficjalnego źródła takich danych.

Analiza dotyczy danych z okresu 4.03.2020 do 28.03.2020.

##Import potrzebnych bibliotek
"""

import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""##Wczytanie danych"""

ConfirmedCases_raw=pd.read_csv('https://raw.githubusercontent.com/kk197/KoronaScience_Raport/master/confirmed_cases.csv')
Deaths_raw=pd.read_csv('https://raw.githubusercontent.com/kk197/KoronaScience_Raport/master/deaths.csv')
Voivodeships_info=pd.read_csv('https://raw.githubusercontent.com/kk197/KoronaScience_Raport/master/voivodeships_info.csv')

"""##Utworzenie tabeli, w której dla każdej daty podana jest całkowita dotychczasowa liczba zachorowań w danym województwie"""

#funkcja umożliwiająca utworzenie tabeli, gdzie dla każdej kolejnej daty liczba przypadków jest sumą nowych przypadków oraz wcześniejszych przepadków
def sumcases(raw):
  total = pd.DataFrame.copy(raw)
  for x in range(raw.shape[0]):
    for y in range(1,raw.shape[1]):
      if x>0:
        total.at[x,total.columns[y]] = total.values[x-1][y] + raw.values[x][y]
  total=total.drop(columns=["Daily","Total"])
  return total

Deaths_total=sumcases(Deaths_raw)
ConfirmedCases_total=sumcases(ConfirmedCases_raw)

"""##Wykres wzrostu zachorowań dla poszczególnych województw"""

plt1=ConfirmedCases_total.plot(figsize=(20,15), marker='o', title='Przypadki potwierdzone wykrycia COVID-19', grid="True",x="Date")
plt1.set_xlabel('Województwo')
plt1.set_ylabel('Przypadki zachorowań')

"""###W skali logarytmicznej"""

plt2=ConfirmedCases_total.plot(figsize=(20,15), marker='o', title='Przypadki potwierdzone wykrycia COVID-19', grid="True",x="Date", logy=True)
plt2.set_xlabel('Województwo')
plt2.set_ylabel('Przypadki zachorowań')

"""##Wykres wzrostu liczby śmiertelnych przypadków dla poszczególnych województw"""

plt3=Deaths_total.plot(figsize=(15,8), marker='o', title='Przypadki śmiertelne z powodu COVID-19', grid="True",x="Date")
plt3.set_xlabel('Województwo')
plt3.set_ylabel('Przypadki śmiertelne')

"""##Wykresy udziału liczby zachorowań oraz zgonów dla poszczególnych województw w stosunku do całkowitej liczby zachorowań"""

#funkcja pomocnicza do obliczenia stosunku liczby przypadków w danym województwie do sumy przypadków w kraju
def todaypercentage(total,raw):
  todayPercentage = total.tail(1)
  todayPercentage = todayPercentage.set_index("Date")
  todayPercentage1 = todayPercentage.values[-1,:]/raw.values[-1,-1]
  df = pd.DataFrame({'cases': todayPercentage1},
                    index=todayPercentage.columns).sort_values(by='cases')
  return df

Confirmed_today_percentage=todaypercentage(ConfirmedCases_total,ConfirmedCases_raw)
Deaths_today_percentage=todaypercentage(Deaths_total,Deaths_raw)

Confirmed_today_percentage_plot = Confirmed_today_percentage.plot.pie(y='cases', figsize=(15, 15), legend=False, autopct='%1.0f%%', title="Udział liczby zachorowań dla poszczególnych województw w stosunku do całkowitej liczby zachorowań")
Deaths_today_percentage_plot = Deaths_today_percentage.plot.pie(y='cases', figsize=(15, 15), legend=False, autopct='%1.0f%%', title="Udział liczby przypadków śmiertelnych dla poszczególnych województw w stosunku do całkowitej liczby przypadków śmiertelnych")

"""##Połączenie najaktualniejszych danych z informacjami o województwach"""

def mergewithinfo(info, total):
  total=total.tail(1).drop(columns="Date").transpose().set_axis(['Cases'], axis=1, inplace=False)
  total=total.reset_index()
  merged = info.merge(total,left_on='Voivodeships',right_on='index')
  merged=merged.set_index("index")
  return merged

Confirmed_info=mergewithinfo(Voivodeships_info,ConfirmedCases_total)
Deaths_info=mergewithinfo(Voivodeships_info,Deaths_total)

"""##Liczba zachorowań przypadająca na 100 000 mieszkańców województwa"""

per100000=(Confirmed_info["Cases"]/Confirmed_info["Population"])*100000
per100000=per100000.sort_values(ascending=False)
plt=per100000.plot.bar(title='Liczba zachorowań przypadająca na 100 000 mieszkańców')
plt.set_xlabel('Województwo')
plt.set_ylabel('Przypadki zachorowań')

"""##Analiza wpływu liczby ludności danego województwa na liczbę zachorowań
Przypadki zachorowań na 100 000 mieszkańców zostały posortowane według całkowitej liczby ludności danego województwa.

Z poniższego wykresu wynika, że na dzień dzisiejszy nie jest mocno zauważalna zależność pomiędzy tymi parametrami. Widoczne jest jednak, że trzy województwa z najwyższymi liczbami przypadków zachorowań są w pierwszej połowie tych najbardziej zaludnionych.
"""

#funkcja do rysowania wykresów z możliwością posortowania według danego parametru i wyświetleniu wyników w odniesieniu do liczby zachorowań/100000 mieszkańców województwa
def plotcases(sortby, info, tit):
  data=info.sort_values(by=sortby, ascending=False)
  data2=(data["Cases"]/data["Population"])*100000
  plt=data2.plot.bar(title=tit)
  plt.set_xlabel('Województwo')
  plt.set_ylabel('Przypadki zachorowań')
  return plt

plotcases("Population", Confirmed_info, 'Wpływ liczby ludności na liczbę zachorowań')

"""##Analiza wpływu gęstości zaludnienia na liczbę zachorowań
Przypadki zachorowań na 100 000 mieszkańców zostały posortowane według gęstości zaludnienia danego województwa.

Z poniższego wykresu wynika, że na dzień dzisiejszy nie jest mocno zauważalna zależność pomiędzy tymi parametrami. Widoczne jest jednak, że trzy województwa z najwyższymi liczbami przypadków zachorowań są w pierwszej połowie tych o największej gęstości zaludnienia.
"""

plotcases("Pop. per km^2", Confirmed_info, 'Wpływ gęstości zaludnienia na liczbę zachorowań')

"""##Analiza wpływu poziomu urbanizacji na liczbę zachorowań
Przypadki zachorowań na 100 000 mieszkańców zostały posortowane według poziomu urbanizacji danego województwa.

Z poniższego wykresu wynika, że na dzień dzisiejszy nie jest mocno zauważalna zależność pomiędzy tymi parametrami. Widoczne jest jednak, że trzy województwa z najwyższymi liczbami przypadków zachorowań są w pierwszej połowie tych o największym poziomie urbanizacji.

Prawdopodobnie, za jakiś czas, zacznie być zauważalna zależność pomiędzy tymi parametrami, ponieważ mieszkańcy dużych miast są bardziej narażeni na kontakt z obcymi osobami min. w komunikacji miejskiej.
"""

plotcases("Urbanization", Confirmed_info, 'Wpływ poziomu urbanizacji na liczbę zachorowań')

"""##Analiza wpływu PKB na liczbę zachorowań
Przypadki zachorowań na 100 000 mieszkańców zostały posortowane według poziomu PKB danego województwa.

Z poniższego wykresu wynika, że na dzień dzisiejszy nie jest mocno zauważalna zależność pomiędzy tymi parametrami. Widoczne jest jednak, że trzy województwa z najwyższymi liczbami przypadków zachorowań są w pierwszej połowie tych o największym poziomie PKB.
"""

plotcases("Gross domestic product", Confirmed_info, 'Wpływ PKB na liczbę zachorowań')

"""##Wnioski
Niestety nie udało wyciągnąć się jakichś jednoznacznych wniosków z przeprowadzonych analiz. Badanie umożliwiło jednak utworzenie narzędzia, które może być pomocne przy analizowaniu danych po zakończeniu epidemii COVID-19, gdy danych do analizy będzie więcej. 

Nie analizowałam dokładnie statystyk dotyczących liczby przypadków śmiertelnych, ponieważ uznałam, że ich liczba jest zbyt mała.
"""