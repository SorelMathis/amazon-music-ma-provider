# Amazon Music MA Provider

Ce dépôt est un scaffold de développement autonome pour un fournisseur Music Assistant d'Amazon Music, sans modifier l'installation officielle Music Assistant déjà en place.

Ce que ce dépôt n'est pas :
- ce n'est pas une intégration officielle Amazon Music Unlimited,
- ce n'est pas un fournisseur validé par Amazon,
- ce n'est pas une intégration de lecture réelle exploitable dans un conteneur MA sans une API ou un accès autorisé côté Amazon.

Ce que ce dépôt est :
- un squelette technique compatible avec l'architecture de fournisseur Music Assistant,
- une base de développement isolée hors conteneur MA,
- une couche de validation des secrets, des sessions et des URL,
- un point d'entrée pour une intégration réelle à condition de disposer d'un flux Amazon autorisé et stable.

Audit technique de conformité
- Le rôle du package `custom_providers/amazon_music` est de reproduire le schéma de chargement d'un fournisseur Music Assistant : `manifest.json` + `__init__.py` + optionnel `setup_flow.py`.
- Le `setup()` du module fournisseur doit respecter la signature attendue par Music Assistant : `setup(mass, manifest, config)`.
- Un fournisseur réel Music Assistant hérite de `MusicProvider` et doit implémenter les méthodes de catalogue/lecture selon les fonctionnalités déclarées. Ce repo ne prétend pas les avoir validées avec la stack MA officielle, car l'API Amazon réelle manque encore.

Sécurité
- Aucun mot de passe Amazon n'est stocké dans le dépôt.
- Les tokens ou sessions sont stockés dans un support utilisateur sécurisé, via `keyring` si disponible, sinon dans un fichier local chiffré par convention et protégé (permissions restrictive 600).
- Les données de démonstration ne sont jamais présentées comme des accès Amazon réels.

URL et flux de streaming
- Les URL de démonstration ne doivent pas être acceptées comme des flux Amazon réels.
- Les URL `mock://...` sont explicitement marquées comme des flux de test local uniquement.
- Les URL `https://...` non contrôlées par Amazon ne sont pas considérées comme valides pour un flux de production.

État réel du projet
- Fonctionnel/testé : validation des identifiants, gestion de session expirée, stockage sécurisé, validation de flux mockés, intégration de base du package et tests automatisés.
- Implémenté, mais non validé contre Amazon : intégration de service réel, authentification Amazon et lecture de flux réels.
- Bloqué pour la lecture réelle : accès officiel et autorisé à Amazon Music Unlimited.

Installation isolée du paquet de test
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e .
pytest -q
```

Cette commande ne touche pas le conteneur Music Assistant existant.
