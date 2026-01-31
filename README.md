# RobyBot

Un bot Discord complet pour la gestion de la communauté Robynet, avec système de rôles, vérification, XP, culture générale et notifications YouTube.

## Fonctionnalités

### 1. **Gestion des Rôles** (`gestionnaireRole.py`)
- Attribution automatique d'un rôle "Non vérifié" à l'arrivée d'un nouveau membre
- Réactions pour obtenir des rôles personnalisés via emojis
- Système de vérification des membres avec messages de règlement
- Stockage des configurations par serveur en SQLite

### 2. **Système d'XP** (`systemeXP.py`) `[Work in progress]`
- Gain de **2 XP** par message envoyé
- Gain de **1 XP par minute** passée en vocal
- Attribution automatique de rôles selon le niveau atteint
- Annonces de niveau-up dans le salon dédié

### 3. **Culture Générale** (`gestionnaireCultureG.py`)
- Question quotidienne posée automatiquement
- Système de sondage avec réactions emoji
- Stockage des questions en SQLite avec historique des réponses

### 4. **Notifications YouTube** (`gestionnaireYoutube.py`)
- Surveillance de chaînes YouTube configurées
- Vérification des nouvelles vidéos toutes les 10 minutes
- Notifications automatiques dans le salon dédié
- Gestion de plusieurs chaînes

### 5. **Anti-Spam** (`gestionnaireAntiSpam.py`) `[Work in progress]`
- Détection des spammeurs
- Bannissement automatique des nouveaux membres qui spamment
- Logs des violations

### 6. **Commandes d'Aide** (`gestionnaireAide.py`)
- Informations sur le serveur et le bot
- Aide sur les commandes disponibles


## Structure du Projet

```
RobyBot/
├── main.py                     
├── requirements.txt            
├── .env                         
├── bot.db                       
├── gestionnaireRole.py        
├── systemeXP.py                
├── gestionnaireCultureG.py   
├── gestionnaireYoutube.py     
├── gestionnaireAntiSpam.py    
├── gestionnaireAide.py          
├── gestionnaireCommande.py     
├── dictionnaireEmojies.py     
├── web.py                      
├── identifiants.json            
├── questions.json               
├── suiviYt.json                 
└── docs/
    └── todolist.txt             
```

## Améliorations Futures

- [ ] Stockage de l'XP
- [ ] Système de concours/giveaways
- [ ] Rôle spécial pour les boosters
- [ ] Dashboard web pour configuration
- [ ] Backup automatique de la base de données
- [ ] Commandes d'administration avancées
- [ ] Système de permissions modulable

## Auteur

Bot créé par **Shin60** pour la communauté Robynet