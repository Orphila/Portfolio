import streamlit as st  
import plotly.express as px  

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Comparatif portfolio/ETF ", 
                   page_icon=":bar_chart:", 
                   layout="wide")
#Jour ouvrés----
def liste_jours_ouvrés():
    from dateutil.parser import parse
    from dateutil.rrule import rrule, DAILY
    from dateutil.relativedelta import relativedelta
    from dateutil.relativedelta import MO, TU, WE, TH, FR
    
    dtstart = parse('2022-01-01')
    list_jours_ouvres = list(
        map(
            lambda x: x.date(),
            rrule(DAILY, dtstart=dtstart, until=dtstart + relativedelta(months=24, day=1, days=-1),
                  byweekday=[MO, TU, WE, TH, FR])
        )
    )
    
    ouvrés=[str(k)[:10] for k in list_jours_ouvres]
    return ouvrés
# ---- MAINPAGE ----
st.title(":bar_chart: Comparatif portfolio/ETF pour 1000$ investis")
st.markdown("##")
date_debut="2022-4-20"

date_fin=liste_jours_ouvrés()[-1]

if date_fin in liste_jours_ouvrés():
    #--------------------------création du dataset avec yahoo finance--------------
    import yfinance as yf
    #définition ticker
    #ETF
    cac_40='^FCHI'
    BT_C='BTC=F'
    SP_500='ES=F'
    
    #Cryptos du portfolio
    LINK='LINK-USD'
    ETH='ETH-USD'
    AVAX='AVAX-USD'
    TH='THETA-USD'
    #récupération données
    cac40=yf.Ticker(cac_40)
    BTC=yf.Ticker(BT_C)
    SP500=yf.Ticker(SP_500)
    ETF=[cac40,SP500,BTC]
    
    LINK=yf.Ticker(LINK)
    ETH=yf.Ticker(ETH)
    AVAX=yf.Ticker(AVAX)
    TH=yf.Ticker(TH)
    
    CRYPTOS=[LINK,ETH,AVAX,TH]
    #récupéation prix sur un pas journalier sur la péiode voulue
    #date_debut='2022-4-27'
    #date_fin='2022-12-3'
    #LA DATE DOIT ÊTRE UN JOUR OUVERT
    for i in range(len(ETF)):
        ETF[i]=ETF[i].history(period='1d',
                          start=date_debut,
                          end= date_fin)['Close']
    for j in range(len(CRYPTOS)):
        CRYPTOS[j]=CRYPTOS[j].history(period='1d',
                          start=date_debut,
                          end= date_fin)['Close']
    def liste_index(actif):
        "lister les dates"
        liste_dates=[str(actif.index.tolist()[k])[:10] for k in range(len(actif))]
        return liste_dates
    liste_ref=liste_index(CRYPTOS[0]) #N'importe quelle liste de cryptos btc exclu fait l'affaire
    
    
    def mise_a_niveau(liste, num):
        """Fill valeur précédente si le jour concerné était fermé"""
        A = ETF[num]
        ref = liste_ref
        liste_dates = [str(A.index.tolist()[k])[:10] for k in range(len(A))]
        liste = liste.tolist()
        k = 0
        #u=len(ref)-len(liste_dates)
        #for k in range(u):
         #   liste_dates.append('palier à la diffde len')
        while k < len(ref) - 1:
            if liste_dates[k] != ref[k]:
                liste.insert(k, liste[k])
                liste_dates.insert(k, ref[k])
            else:
                k += 1
        return (liste)
    
    #groupement des difféents dataset en gardant des entiers
    import pandas as pd
    investissement_depart=1000
    #Mettre la valeur de départ en atttribut aussi. Fonction conversion avec
    
    
    for k in range(len(ETF)):
        #Mise à  niveau des dates d'ETF
        ETF[k] = mise_a_niveau(ETF[k], k)
    
    # Conversion à  l'investissement
    a = [int(k * investissement_depart / 6715.1) for k in ETF[0]]
    b = [int(k * investissement_depart / 4559) for k in ETF[1]]
    d = [int(20 * CRYPTOS[0][k] + 0.1 * CRYPTOS[1][k] + .005 * ETF[2][k] + 2 * CRYPTOS[2][k] + 11 * CRYPTOS[3][k]) for k in
         range(len(CRYPTOS[2]))]
    # On met la valeur proportionnel du BTC aprÃ¨s avoir fais le calcul pour le pf
    c = [int(k * investissement_depart / 41559) for k in ETF[2]]
    
    df = pd.DataFrame(zip(a, b, c, d)
                      , index=liste_ref
                      , columns=['cac40', 'S&P500', 'BTC', 'Portfolio'])
    
    #--------------Fonctions KPI-------------------------------
    def perf(indice):
        ret=(indice[-1]-indice[0])/investissement_depart
        return str(round(100*ret,1))+'%'
    def gain(indice):
        ret=(indice[-1]-indice[0])/investissement_depart
        return str(ret*investissement_depart)+'$'
    def correlation(x,y):
        
        mX = sum(x)/len(x)
        mY = sum(y)/len(y)
        cov = sum((a - mX) * (b - mY) for (a,b) in zip(x,y)) / len(x)
        stdevX = (sum((a - mX)**2 for a in x)/len(x))**0.5
        stdevY = (sum((b - mY)**2 for b in y)/len(y))**0.5
        if cov==0 or stdevX==0 or stdevY==0:
            return("En attente des dates")
        result = round(cov/(stdevX*stdevY),3)
        return(str(round(result*100,1))+'%')
    
    
    # TOP KPI's
    indice_perf = pd.DataFrame({'Indices':['cac40','S&P50','BTC','Portfolio'],
                               'Performances' :[perf(df['cac40']),
                                                perf(df['S&P500']),
                                                perf(df['BTC']),
                                                perf(df['Portfolio'])]})
    
    valeur_actuelle = str(df['Portfolio'][-1])+'$'
    #On fera la même pour les autres actifs
    corrélation_BTC = correlation(df['Portfolio'], df['BTC'])
    
    left_column, right_column = st.columns(2)
    
    left_column.metric(label='valeur du portfolio',
                        value=valeur_actuelle,
                        delta=perf(df['Portfolio']))  
    
    right_column.metric(label='Corrélation du portfolio au BTC',
                        value=corrélation_BTC) 
    
    st.markdown("""---""")
    
    #----graphs----
    new_df=df.assign(Date=liste_ref)
    courbe = px.line(new_df,x='Date', y=['cac40',
                                     'S&P500',
                                     'BTC',
                                     'Portfolio'],
                     title='Comparatif portfolio/indices',
                     width=750,
                     labels={
                         "value" : "valeur investissement ($)",
                         "x" : "Dates",
                         "variable" : "Indices"
                     })
    
    #Rapport crypto/invest
    CR=[0,0,0,0,0]
    CR[0]=[20 * CRYPTOS[0][k] for k in range(len(CRYPTOS[0]))]
    CR[1]=[0.1 * CRYPTOS[1][k] for k in range (len(CRYPTOS[1]))]
    CR[2]=df['BTC'].tolist()
    CR[3]=[2 * CRYPTOS[2][k] for k in range (len(CRYPTOS[2]))]
    CR[4]=[11 * CRYPTOS[3][k] for k in range (len(CRYPTOS[3]))]
    
    
    X=[CR[k][-1] for k in range(len(CR))]
    NAMES=['LINK','ETH','BTC','AVAX','THETER']
    fromage = px.pie(values=X, names=NAMES,title="Répartition du portfolio",width=450)
    left_column, right_column = st.columns([2,1])
    left_column.plotly_chart(courbe)
    right_column.plotly_chart(fromage)
    
    st.markdown("""---""")
    
    a,b,c,d=st.columns(4)
    
    a.metric(label='Bénéfice cac40',
             value=gain(df['cac40']),
             delta=perf(df['cac40']))
    b.metric(label='Bénéfice S&P500',
             value=gain(df['S&P500']),
             delta=perf(df['S&P500']))
    c.metric(label='Bénéfice BTC',
             value=gain(df['BTC']),
             delta=perf(df['BTC']))
    d.metric(label='Bénéfice Portfolio',
             value=gain(df['Portfolio']),
             delta=perf(df['Portfolio']))       
             

