# 1. Arborescence du Projet (Architecture des dossiers & fichiers)
Pour garantir un code propre, réutilisable et facile à transférer sur la Sandbox Jupyter, voici la structure de dossiers standard recommandée pour une application agentique avec LangGraph

```bash
assurhabitat_ai/
│
├── data/                         # Données brutes et documents de référence
│   ├── contrat_garantie.pdf      # Contrat d'assurance Habitation
│   ├── processus_gestion.pdf     # Processus métier de gestion des sinistres
│   ├── images/                   # Photos de test (dégâts, effractions, etc.)
│   └── golden_dataset.csv        # Dataset final consolidé (à générer)
│
├── src/                          # Code source Python modularisé
│   ├── __init__.py
│   ├── config.py                 # Hyperparamètres, chemins, configuration des LLM/VLM
│   ├── state.py                  # Schéma de l'état partagé LangGraph (GraphState)
│   │
│   ├── agents/                   # Logique individuelle de chaque agent
│   │   ├── __init__.py
│   │   ├── declaration_agent.py  # Agent 1 : Collecte & Complétude
│   │   ├── validation_agent.py   # Agent 2 : Vérification du contrat (RAG/Règles)
│   │   ├── expertise_agent.py    # Agent 3 : Analyse VLM des photos
│   │   └── orchestration.py      # Routeur / Sélection des prestataires
│   │
│   ├── prompts/                  # Prompts système de chaque agent
│   │   ├── declaration_prompts.py
│   │   ├── validation_prompts.py
│   │   └── expertise_prompts.py
│   │
│   └── graph.py                  # Construction du Workflow / StateGraph LangGraph
│
├── notebook_sandbox.ipynb        # Notebook principal à exécuter sur la Cloud Sandbox
├── requirements.txt              # Dépendances Python (langgraph, langchain, ollama, etc.)
└── README.md                     # Instructions d'exécution
```

# 2. 🚀 Étape 1 : Définir le schéma d'état (GraphState) et configurer l'Agent Déclaration
L'agent Déclaration a un rôle précis :

1. Recevoir le message initial de l'assuré (et les pièces jointes/photos).

2. Vérifier la complétude des 3 éléments indispensables :

    * Date du sinistre

    * Description détaillée du sinistre

    * Photos/Pièces jointes

3. Extraire ces éléments sous forme structurée sans juger de leur validité contractuelle à ce stade.

# 3.🛠️ Codons la base sur ton PC
1. Fichier requirements.txt
Créons le fichier de dépendances pour ton environnement local (à installer via pip install -r requirements.txt) :

Plaintext
langgraph>=0.2.0
langchain-core>=0.3.0
langchain-community>=0.3.0
pydantic>=2.0
pandas
pillow
2. Fichier src/state.py
Ce fichier définit la mémoire partagée (State) transmise d'agent en agent tout au long du workflow LangGraph.

``` bash
Python
from typing import TypedDict, List, Optional, Dict, Any

class SinistreState(TypedDict):
    # Informations fournies en entrée
    raw_declaration: str            # Texte de la déclaration client
    image_paths: List[str]          # Chemins vers les images jointes

    # Extractions réalisées par l'Agent Déclaration
    famille_sinistre: Optional[str] # Dégât des eaux, Incendie, Cambriolage
    date_sinistre: Optional[str]    # Date extraite
    description: Optional[str]      # Description résumée
    has_photos: bool                # True si au moins une photo est jointe
    declaration_complete: bool      # True si Date + Description + Photos sont présents
    champs_manquants: List[str]     # Liste des éléments absents (ex: ["date"])

    # Informations de Validation (Agent 2)
    garantie_valide: Optional[bool]
    motif_refus: Optional[str]
    delai_respecte: Optional[bool]

    # Informations d'Expertise (Agent 3 - VLM)
    analyse_image: Optional[str]
    estimation_degats: Optional[str]

    # Orchestration & Résolution
    prestataire_recommande: Optional[str]  # Plombier, Vitrier, Expert, etc.
    statut_dossier: str                     # EN_COURS, CLOTURE, TRANSMIS_EXPERT
```

# 3. Installer les packages necessaires 
1. Installer poetry pour gérer les dépendances "pip install petry"
2. installer toutes les dépendances dont on aura besoin avec "poetry install"

# 4. Créer les codes des agents 
## 4.1. Agent Declaration
- **Rôle** : 
    L'agent IA Déclaration a pour objectif de récupérer l'ensemble des informations nécessaires afin de poursuivre le processus de prise en charge du sinistre. Plus précisément, il doit :

    1.  **Collecter les éléments clés** conformément au processus de gestion, c'est-à-dire s'assurer de la présence de la date, des informations sur le sinistre et des photos.
    2. **Vérifier la complétude** des informations demandées (en s'assurant que tous les éléments requis sont bien présents).
    3. À cette étape, il n'est **pas attendu de valider les informations** récoltées (comme vérifier la validité des garanties ou juger du bien-fondé du dossier), mais uniquement de s'assurer de leur présence pour alimenter la suite du workflow.

## 4.2. Agent validation
- **Rôle** : 
    1. Récupérer les informations extraites par l'Agent Déclaration.
    2. Vérifier si le sinistre entre dans le cadre du Contrat de garantie habitation :

        * Dégâts des eaux / Incendie : Déclaration sous 5 jours ouvrés max.

        * Vol / Cambriolage : Déclaration sous 2 jours ouvrés max + Dépôt de plainte requis.

    3. Déterminer si le sinistre est VALIDE, REFUSÉ (ex: hors délai / exclusion) ou EN_ATTENTE_PIECES (ex: manque le dépôt de plainte).

## 4.3. Agent Expertise
- **Rôle** : Évaluer les dommages techniques et chiffrer l'indemnisation.

- **Mission** : Analyser les photos du sinistre, estimer les coûts de réparation, calculer le montant accordé selon les garanties et rédiger un rapport technique. Il ne donne pas de décision finale à l'assuré et délègue la suite au conseiller humain.

## 4.4. Orchestrateur Langraph Langchain
Ce fichier définit les nœuds (nos agents) et la logique d'orientation (edges/routeurs) selon l'avancement du dossier.

- **Rôle** : Piloter la chaîne de traitement et orienter les dossiers vers les interlocuteurs appropriés (conseiller, plombier, vitrier, expert).

- **Comment fonctionne la chaîne d'exécution ?**
1. Entrée : L'assuré soumet sa déclaration initiale.
2. Nœud Déclaration : Contrôle si la date, la description et au moins une photo sont fournies. Si incomplet $\rightarrow$ fin de chaîne.
3. Nœud Validation : Contrôle les garanties du contrat et les délais légaux. Si non couvert $\rightarrow$ fin de chaîne avec notification.
4. Nœud Expertise : Analyse la photo via VLM, estime les coûts et rédige le rapport pour le conseiller.
5. Orchestration : Sélectionne le prestataire adéquat (Plombier, Serrurier, Expert incendie).



# 5. Structure & Métriques du Golden Dataset
Pour chaque exemple du jeu de test, le projet exige d'évaluer les métriques suivantes :

1. Agent Déclaration : Taux de complétude des informations demandées (Complétude_Declaration).

2. Agent Validation : Bon usage factuel du contrat et respect des délais (Conformite_Contrat).

3. Agent Expertise : L'évaluation est réservée aux experts humains (aucune métrique automatique).

4. Agent Orchestrateur : Précision du prestataire/interlocuteur identifié (Precision_Prestataire).

# 6. Tester la pipeline en local 

Le script de test local **test_local.py** simule l'exécution du workflow **LangGraph** sur ton PC avec des données de test (mocks), sans nécessiter de charger de modèle lourd en VRAM.