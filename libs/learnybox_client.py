"""
Nom du module : learnybox_client.py
Description   : Client Python pour l'API LearnyBox v2.
                Gere l'authentification OAuth (api_key -> access_token)
                et fournit des methodes pour interroger les endpoints.
Auteur        : Meza-Project
Date          : 2026-02-23

Dependances :
    - requests (pip install requests)

Usage :
    from libs.learnybox_client import LearnyBoxClient

    client = LearnyBoxClient(api_key="...", subdomain="mezaelle-hkc")
    evaluations = client.get_user_evaluations(user_id="123")
"""

import logging
import time

import requests

logger = logging.getLogger(__name__)


class LearnyBoxAPIError(Exception):
    """Erreur retournee par l'API LearnyBox."""

    def __init__(self, status_code, message, response=None):
        self.status_code = status_code
        self.message = message
        self.response = response
        super().__init__(f"[{status_code}] {message}")


class LearnyBoxClient:
    """Client pour l'API LearnyBox v2."""

    API_VERSION = "v2"
    TOKEN_ENDPOINT = "/api/v2/oauth/token/"
    TOKEN_REVOKE_ENDPOINT = "/api/v2/oauth/token/revoke/"

    def __init__(self, api_key, subdomain):
        """
        Args:
            api_key: Cle API LearnyBox (generee dans Outils > API).
            subdomain: Sous-domaine LearnyBox (ex: 'mezaelle-hkc').
        """
        self.api_key = api_key
        self.subdomain = subdomain
        self.base_url = f"https://{subdomain}.learnybox.com"
        self.access_token = None
        self.refresh_token = None
        self._session = requests.Session()

    def authenticate(self):
        """Obtient un access_token via la cle API.

        Envoie la cle API dans le header X-API-Key et grant_type en POST.
        Le token obtenu est valide 24 heures.
        """
        url = f"{self.base_url}{self.TOKEN_ENDPOINT}"
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {
            "grant_type": "access_token",
        }
        logger.info("Authentification aupres de %s", url)
        resp = self._session.post(url, data=payload, headers=headers)

        if resp.status_code != 200:
            raise LearnyBoxAPIError(
                resp.status_code,
                f"Echec d'authentification: {resp.text}",
                response=resp,
            )

        data = resp.json()
        self.access_token = data.get("access_token") or data.get("data", {}).get("access_token")
        self.refresh_token = data.get("refresh_token") or data.get("data", {}).get("refresh_token")

        if not self.access_token:
            raise LearnyBoxAPIError(
                resp.status_code,
                f"Pas d'access_token dans la reponse: {data}",
                response=resp,
            )

        self._session.headers.update({
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        })
        logger.info("Authentification reussie (token valide 24h).")
        return self.access_token

    def refresh_access_token(self):
        """Renouvelle l'access_token avec le refresh_token.

        Le refresh_token est valide 1 mois.
        Necessite le header X-API-Key et grant_type=refresh_token en POST.
        """
        if not self.refresh_token:
            raise LearnyBoxAPIError(0, "Pas de refresh_token disponible.")

        url = f"{self.base_url}{self.TOKEN_ENDPOINT}"
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        resp = self._session.post(url, data=payload, headers=headers)

        if resp.status_code != 200:
            raise LearnyBoxAPIError(
                resp.status_code,
                f"Echec du refresh token: {resp.text}",
                response=resp,
            )

        data = resp.json()
        self.access_token = data.get("access_token") or data.get("data", {}).get("access_token")
        new_refresh = data.get("refresh_token") or data.get("data", {}).get("refresh_token")
        if new_refresh:
            self.refresh_token = new_refresh

        self._session.headers["Authorization"] = f"Bearer {self.access_token}"
        logger.info("Token renouvele.")
        return self.access_token

    def _request(self, method, path, params=None, json_data=None, retry_auth=True):
        """Effectue une requete HTTP vers l'API.

        Si le token est expire (498), tente un refresh puis re-essaie.
        LearnyBox retourne HTTP 498 "Token expired/invalid" quand le
        Bearer token n'est plus valide.
        """
        if not self.access_token:
            self.authenticate()

        url = f"{self.base_url}/api/{self.API_VERSION}/{path.lstrip('/')}"
        logger.debug("%s %s params=%s", method, url, params)

        resp = self._session.request(method, url, params=params, json=json_data)

        # Token expire (498) -> refresh et retry
        if resp.status_code == 498 and retry_auth:
            logger.info("Token expire (498), tentative de refresh...")
            try:
                self.refresh_access_token()
            except LearnyBoxAPIError:
                logger.info("Refresh echoue, re-authentification complete...")
                self.authenticate()
            return self._request(method, path, params=params, json_data=json_data, retry_auth=False)

        if resp.status_code >= 400:
            raise LearnyBoxAPIError(
                resp.status_code,
                f"{method} {url} -> {resp.text}",
                response=resp,
            )

        return resp.json()

    def get(self, path, params=None):
        """Requete GET."""
        return self._request("GET", path, params=params)

    def post(self, path, data=None):
        """Requete POST."""
        return self._request("POST", path, json_data=data)

    def get_all_pages(self, path, params=None):
        """Recupere toutes les pages d'un endpoint pagine.

        L'API LearnyBox utilise offset/limit pour la pagination.
        """
        if params is None:
            params = {}
        params.setdefault("limit", 50)
        params.setdefault("offset", 0)

        all_items = []
        while True:
            data = self.get(path, params=params)

            items = data.get("data", [])
            if isinstance(items, dict):
                items = [items]
            all_items.extend(items)

            total = data.get("total", 0)
            if len(all_items) >= total or not items:
                break

            params["offset"] += params["limit"]
            time.sleep(0.2)  # rate-limiting

        return all_items

    # ── Endpoints Evaluations ────────────────────────────────────────

    def get_user_evaluations(self, user_id):
        """Liste les evaluations d'un utilisateur.

        GET /api/v2/evaluation/user/{user_id}/
        """
        return self.get(f"evaluation/user/{user_id}/")

    def get_evaluation_responses(self, evaluation_id, user_id):
        """Liste les reponses a une evaluation pour un utilisateur.

        GET /api/v2/evaluation/{evaluation_id}/user/{user_id}/
        """
        return self.get(f"evaluation/{evaluation_id}/user/{user_id}/")

    # ── Endpoints Formations (utilitaire) ────────────────────────────

    def get_formation_members(self, formation_id):
        """Liste les membres d'une formation.

        GET /api/v2/formation/{formation_id}/members/
        """
        return self.get_all_pages(f"formation/{formation_id}/members/")

    # ── Endpoint Contacts (utilitaire) ───────────────────────────────

    def get_contacts(self):
        """Liste tous les contacts.

        GET /api/v2/mail/contacts/
        """
        return self.get_all_pages("mail/contacts/")

    def revoke_token(self):
        """Revoque l'access_token courant."""
        if not self.access_token:
            return
        url = f"{self.base_url}{self.TOKEN_REVOKE_ENDPOINT}"
        self._session.post(url, json={"access_token": self.access_token})
        self.access_token = None
        logger.info("Token revoque.")
