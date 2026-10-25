# Amazon Music MA Provider

Ce dépôt est un scaffold de développement autonome pour un fournisseur Music Assistant d'Amazon Music, sans modifier l'installation officielle Music Assistant déjà en place.

Ce que ce dépôt n'est pas :
- ce n'est pas un fournisseur Amazon Music Unlimited officiellement supporté par Amazon,
- ce n'est pas une intégration de lecture réelle prête à l'emploi,
- ce n'est pas une intégration avec le runtime officiel Music Assistant installé dans ce dépôt.

Ce que ce dépôt est :
- un squelette technique autonome pour préparer une intégration Music Assistant,
- une base de développement isolée hors conteneur Docker MA,
- une couche de validation de sessions, sécrets et flux de test,
- un point de départ pour une intégration réelle, sous réserve d'un accès Amazon autorisé, documenté et stable.

Compatibilité technique ciblée
- Le runtime officiel Music Assistant a un contrat de fournisseur basé sur `MusicProvider` (voir `music_assistant/models/music_provider.py`) et sur le mécanisme de chargement de manifestes dans `music_assistant/mass.py`.
- Ce dépôt ne prétend pas être chargé automatiquement dans la stack MA existante de l'utilisateur ; il est un package autonome d'atelier technique.
- Les fichiers `custom_providers/amazon_music/*.py` et `manifest.json` reproduisent le schéma de découverte d'un fournisseur externe : package du fournisseur + manifest + setup flow, sans importer directement le runtime officiel.
- La validation de compatibilité dans ce dépôt se limite aux imports Python, au contrat local de configuration et aux tests unitaires. Une validation réelle dans le runtime officiel de Music Assistant n'a pas été effectuée ici, car ce dépôt ne contient pas le serveur MA réel.

Sécurité
- Aucun mot de passe Amazon n'est stocké dans le dépôt.
- Les secrets sont gérés via `keyring` si disponible ; sinon dans un fichier local protégé, avec permissions restreintes sur POSIX.
- Les données de démonstration sont explicitement identifiées comme `mock` et ne sont jamais présentées comme des accès Amazon réels.

Validation des flux et URL
- Les URL `mock://...` sont acceptées uniquement en mode mock explicite.
- Les URLs HTTP/HTTPS réelles ne sont acceptées que si une liste de hôtes autorisés est fournie et si le hôte correspond exactement à un hôte autorisé. Aucune URL HTTPS ne doit être acceptée comme preuve de validité Amazon sans cette liste stricte.
- Une URL de test `https://amazon.example.com/stream` est rejetée, parce qu'elle n'est pas un domaine Amazon autorisé et parce que le domaine n'est pas dans la liste de confiance.
- Les domaines de type `amazon.com.site-malveillant.example` ou `music.amazon.com.evil.dev` sont rejetés.

État réel du projet
- Validé ici : validation d'URL, session expirée, stockage sécurisé, séparations mock/réel, import du package fournisseur, tests unitaires.
- Non validé ici : accès réel à Amazon Music Unlimited, authentification Amazon officialisée, catalogue live, lecture audio réelle.
- Bloqué pour la lecture réelle : accès officiel et autorisé à Amazon Music Unlimited.

Environnement de test isolé
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .
pytest -q
```

Cette procédure n'impacte pas le conteneur Docker Music Assistant déjà en fonctionnement.
