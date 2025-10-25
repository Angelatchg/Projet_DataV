import streamlit as st

def render():
    st.title("Conclusion")
    st.markdown("""
    L’analyse menée sur les données de qualité de l’air issues du flux **E2 – Geod’air** met en évidence une **évolution nette des niveaux de pollution atmosphérique** entre la période estivale (août) et la rentrée (septembre).

    Durant **le mois d’août**, les concentrations de polluants tels que le **dioxyde d’azote (NO₂)** et les **particules fines (PM10)** sont globalement **plus faibles et plus stables**.  
    Cette tendance s’explique par une **réduction de l’activité humaine** : trafic routier limité, baisse des émissions industrielles et conditions météorologiques favorables à la dispersion des polluants.

    À l’inverse, **le mois de septembre** marque une **hausse simultanée** des concentrations de **NO₂ et PM10**, accompagnée d’une **corrélation positive** entre ces deux polluants.  
    Les profils horaires révèlent des **pics marqués le matin et en fin de journée**, en lien direct avec les **heures de pointe du trafic**.  
    Les dépassements de seuils de PM10, plus nombreux à la rentrée qu’en été, confirment cet **effet “rentrée”** : la reprise de la circulation, des chantiers et de l’activité urbaine dégrade temporairement la qualité de l’air.

    Bien que les valeurs observées restent sous les seuils réglementaires pour le NO₂, les PM10 dépassent ponctuellement les valeurs indicatives, soulignant la **persistance de sources locales de pollution**.

    Cependant, cette pollution a **diminué en un an**.  
    Cela reflète l’évolution des **comportements et des mentalités**, de plus en plus tournées vers une **mobilité plus durable** et des **modes de transport écologiques**, tels que le covoiturage, le vélo ou les transports en commun.

    ---

    ## Bilan

    Ces résultats montrent clairement que **les activités humaines influencent la qualité de l’air**, avec une **amélioration en période estivale** et une **dégradation mesurable à la rentrée**.  
    Le **trafic routier** apparaît comme le principal facteur explicatif de ces variations.  
    Cette étude illustre la **sensibilité de l’environnement urbain** aux rythmes d’activité humaine et rappelle l’importance de **poursuivre les efforts en faveur d’une mobilité durable**, afin de réduire durablement la pollution atmosphérique en milieu urbain.
    """)
