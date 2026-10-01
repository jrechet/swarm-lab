# AGENTS.md — swarm-lab

Projet d'exercice pour la flotte swarm-bots : un service FastAPI « fortune cookie »
(voir [README.md](README.md) pour le contenu, les commandes et les hooks exercés).

## CI/CD disponibles

Le dépôt est hybride : il vit sur GitHub (référence) et sur la forge Forgejo
`https://forge.jrec.fr/jrechet/swarm-lab` (suiveur).

- **GitHub Actions** (`.github/workflows/`) : `ci.yml` (`pytest -v` sur `ubuntu-latest`,
  dépôt public donc jamais de runner self-hosted pour la CI de PR). Rien ne déploie.
  Suivi d'un run : `gh run list --branch <branche>`, `gh run view <id> --log-failed`.
- **Forge** : `.github/workflows/mirror-to-forge.yml` recopie chaque branche et tag sur la
  forge (secret `FORGE_TOKEN`, posé par le propriétaire). La forge n'exécute que
  `.forgejo/workflows/ci.yml` (mêmes commandes, sur `[self-hosted, jre-server]`) : jamais
  de déploiement. Ne pas y ajouter d'action propre à GitHub.
  Suivi : `ssh jrec.fr '~/dev/server-app/forgejo/forge-tool.sh runs swarm-lab'`.
- **Un seul endroit déploie** : GitHub, tant qu'il reste la référence (ici, rien ne
  déploie). Une modification de la CI se fait dans les deux `ci.yml`, mêmes commandes.
- `tests/test_app.py` contient un test volontairement instable (carburant pour FlakyBot) :
  un rouge isolé n'est pas forcément une régression.
