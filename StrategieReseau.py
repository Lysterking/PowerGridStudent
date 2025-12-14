
from Terrain import Terrain, Case


class StrategieReseau:
    def configurer(self, t: Terrain) -> tuple[int, dict[int, tuple[int, int]], list[tuple[int, int]]]:
        """
        Méthode à surcharger par les stratégies concrètes.
        Retourne :
        - id du noeud d'entrée
        - dictionnaire des noeuds : {id_noeud: (ligne, colonne)}
        - liste des arcs : [(id_noeud_1, id_noeud_2)]
        """
        raise NotImplementedError


class StrategieReseauManuelle(StrategieReseau):
    def configurer(self, t: Terrain) -> tuple[int, dict[int, tuple[int, int]], list[tuple[int, int]]]:
        """
        Stratégie manuelle (à implémenter si besoin).
        Pour l'instant, on renvoie un réseau vide, qui sera invalide.
        """
        return -1, {}, []


class StrategieReseauAuto(StrategieReseau):
    def configurer(self, t: Terrain) -> tuple[int, dict[int, tuple[int, int]], list[tuple[int, int]]]:
        """
        Stratégie automatique simple :
        - crée un noeud sur la case ENTREE,
        - crée un noeud sur chaque case CLIENT,
        - relie chaque noeud CLIENT au noeud d'entrée (graphe en étoile).

        Cette configuration garantit que :
        - le réseau est connexe à partir de l'entrée,
        - chaque client possède un noeud sur sa case,
        - chaque client est accessible depuis l'entrée.
        """

        noeuds: dict[int, tuple[int, int]] = {}
        arcs: list[tuple[int, int]] = []

        entree_id: int = -1
        next_id: int = 0

        # ------------------------------------------------------------------
        # 1 Création des noeuds sur l'ENTREE et les CLIENTS
        # ------------------------------------------------------------------
        for i, ligne in enumerate(t.cases):
            for j, c in enumerate(ligne):
                if c == Case.ENTREE:
                    # On suppose une seule entrée : on ne garde que la première
                    if entree_id == -1:
                        entree_id = next_id
                        noeuds[entree_id] = (i, j)
                        next_id += 1

                elif c == Case.CLIENT:
                    noeuds[next_id] = (i, j)
                    next_id += 1

        # Si aucune entrée n'a été trouvée, on renvoie un réseau vide (invalide)
        if entree_id == -1:
            return -1, {}, []

        # ------------------------------------------------------------------
        # 2) Création des arcs : étoile à partir du noeud d'entrée
        # ------------------------------------------------------------------
        for nid in noeuds.keys():
            if nid == entree_id:
                continue
            # On stocke toujours l'arc sous forme (min, max)
            u, v = sorted((entree_id, nid))
            arcs.append((u, v))

        return entree_id, noeuds, arcs
