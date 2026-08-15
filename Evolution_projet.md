**Exactement, c'est tout à fait ça !** 🎯

Pour récapituler la stratégie hybride très claire sur laquelle nous sommes partis :

---

### 1. 💻 Ce qu'on fait sur ton PC (En amont, sans contrainte de temps)

* **Pourquoi :** Ta carte RTX 3060 (6 Go de VRAM) est parfaite pour coder, prototyper et tester la structure sans consommer la session Cloud.
* **Ce qu'on y fait :**
1. Écrire le code des agents avec **LangGraph** (Déclaration, Validation, Expertise, Orchestration).
2. Définir les prompts, la logique métiers et la structure des données (`GraphState`, modèles Pydantic).
3. Préparer le script d'évaluation et la structure du **Golden Dataset** (les 9 cas de test).
4. Tester localement le code avec un petit modèle léger (via Ollama) ou des *mocks* (réponses simulées).



---

### 2. ☁️ Ce qu'on fait sur la Cloud Sandbox (Pendant les 6h d'accès)

* **Pourquoi :** Tu disposeras de **2 GPUs NVIDIA (48 Go VRAM au total)** pour charger les vrais gros modèles multimodaux (LLM texte + VLM Vision).
* **Ce qu'on y fait :**
1. Charger les scripts/notebooks Python préparés sur ton PC.
2. Charger les modèles lourds en VRAM (ex: `Qwen2-VL` pour les photos et `Llama-3`/`Mistral` pour le texte/RAG).
3. Exécuter l'évaluation complète des agents sur les 9 scénarios du Golden Dataset.
4. **Télécharger immédiatement le fichier `.csv` de résultats** avant la fin des 6 heures.



---

### 🚀 Où en sommes-nous ?

Sur ton PC, nous avons déjà :

1. Défini l'arborescence du projet.
2. Écrit le schéma d'état `SinistreState`.
3. Rédigé le code de l'**Agent IA Déclaration** (`declaration_agent.py`).

Souhaites-tu maintenant passer à la rédaction du 2ème agent : **l'Agent IA Validation** (qui compare la déclaration avec les règles du *Contrat de Garantie*) ?