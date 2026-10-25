# amazon-music-ma-provider

Project de développement autonome pour une intégration Music Assistant d'Amazon Music Unlimited, sans modifier l'installation officielle Music Assistant déjà en place.

Ce dépôt ne prétend pas fournir un accès officiel ou fiable à Amazon Music Unlimited. Il contient :
- un squelette de fournisseur Music Assistant compatible avec l'architecture actuelle,
- un flux de configuration sécurisé,
- un client Python asynchrone avec logique de validation et de streaming mockée,
- des tests automatisés sécurisés,
- une documentation de mise en œuvre et de dépannage.

Principes de sécurité :
- aucun mot de passe Amazon n'est stocké dans le dépôt,
- les tokens sont gérés via le stockage sécurisé du système (keyring) ou un fichier local protégé,
- les appels réels vers Amazon ne sont pas simulés comme réussis.

État réel du projet :
- Implémenté et testé : authentification locale, validation des réponses, recherche et structure du provider.
- Implémenté mais non testé avec un vrai compte Amazon : intégration réelle via Amazon API ou session web.
- Bloqué / non fiable pour un vrai streaming : accès Amazon Music Unlimited réel, car il dépend d'une API officielle ou d'un flux de session validé par Amazon.

Le code ici est destiné à servir de base de développement hors conteneur, sans toucher ni remplacer le conteneur Music Assistant existant.
