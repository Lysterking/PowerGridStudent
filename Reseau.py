from Terrain import Terrain, Case
from StrategieReseau import StrategieReseau, StrategieReseauAuto


class Reseau:
    def __init__(self):
        self.strat = StrategieReseauAuto()
        self.noeuds: dict[int, tuple[int, int]] = {}
        self.arcs: list[tuple[int, int]] = []

        # -1 signifie "non défini"
        self.noeud_entree: int = -1

    # ------------------------------------------------------------------
    # Gestion des éléments du réseau
    # ------------------------------------------------------------------
    def definir_entree(self, n: int) -> None:
        """Définit le noeud d'entrée s'il existe dans le réseau."""
        if n in self.noeuds:
            self.noeud_entree = n
        else:
            # entrée invalide -> on remet à -1
            self.noeud_entree = -1

    def ajouter_noeud(self, n: int, coords: tuple[int, int]) -> None:
        """
        Ajoute un noeud au réseau.
        La clé doit être un entier positif et ne pas déjà exister.
        """
        if n < 0:
            return
        if n in self.noeuds:
            return
        self.noeuds[n] = coords

    def ajouter_arc(self, n1: int, n2: int) -> None:
        """
        Ajoute un arc entre deux noeuds existants.
        Les arcs sont stockés avec (min, max) pour éviter les doublons.
        """
        if n1 > n2:
            n1, n2 = n2, n1

        if n1 not in self.noeuds or n2 not in self.noeuds:
            return

        if (n1, n2) not in self.arcs:
            self.arcs.append((n1, n2))

    def set_strategie(self, strat: StrategieReseau) -> None:
        self.strat = strat

    # ------------------------------------------------------------------
    # Méthodes internes utilitaires
    # ------------------------------------------------------------------
    def _adjacence(self) -> dict[int, set[int]]:
        """Construit la liste d'adjacence du graphe des noeuds."""
        adj: dict[int, set[int]] = {n: set() for n in self.noeuds}
        for u, v in self.arcs:
            if u in adj and v in adj:
                adj[u].add(v)
                adj[v].add(u)
        return adj

    def _noeuds_accessibles_depuis_entree(self) -> set[int]:
        """Renvoie l'ensemble des noeuds accessibles depuis noeud_entree."""
        if self.noeud_entree not in self.noeuds or self.noeud_entree < 0:
            return set()

        adj = self._adjacence()
        visites: set[int] = set()
        a_visiter = [self.noeud_entree]

        while a_visiter:
            courant = a_visiter.pop()
            if courant in visites:
                continue
            visites.add(courant)
            for voisin in adj.get(courant, []):
                if voisin not in visites:
                    a_visiter.append(voisin)

        return visites

    # ------------------------------------------------------------------
    # Validation du réseau
    # ------------------------------------------------------------------
    def valider_reseau(self) -> bool:
        """
        Un réseau est valide si :
        - un noeud d'entrée est défini,
        - tous les noeuds sont accessibles depuis ce noeud d'entrée
          via les arcs du réseau.
        """
        if not self.noeuds:
            return False

        accessibles = self._noeuds_accessibles_depuis_entree()
        # si l'entrée n'est pas valide, l'ensemble sera vide
        if not accessibles:
            return False

        # Tous les noeuds doivent être atteignables
        return len(accessibles) == len(self.noeuds)

    def valider_distribution(self, t: Terrain) -> bool:
        """
        Vérifie que la configuration actuelle permet de distribuer
        l'électricité à tous les clients du terrain.

        Conditions :
        - le réseau doit être valide (connecté à partir de l'entrée),
        - chaque case CLIENT doit porter au moins un noeud,
        - ce noeud doit être relié au noeud d'entrée.
        """
        if not self.valider_reseau():
            return False

        # Ensemble des noeuds accessibles depuis l'entrée
        accessibles = self._noeuds_accessibles_depuis_entree()

        # Inversion du dictionnaire (coords -> id de noeud)
        coords_to_noeud: dict[tuple[int, int], int] = {}
        for nid, coord in self.noeuds.items():
            coords_to_noeud[coord] = nid

        # Parcours de toutes les cases pour trouver les clients
        for i, ligne in enumerate(t.cases):
            for j, c in enumerate(ligne):
                if c == Case.CLIENT:
                    coord = (i, j)
                    # Il doit y avoir un noeud sur cette case
                    if coord not in coords_to_noeud:
                        return False
                    nid_client = coords_to_noeud[coord]
                    # Ce noeud doit être relié à l'entrée
                    if nid_client not in accessibles:
                        return False

        return True

    # ------------------------------------------------------------------
    # Configuration via une stratégie
    # ------------------------------------------------------------------
    def configurer(self, t: Terrain) -> None:
        self.noeud_entree, self.noeuds, self.arcs = self.strat.configurer(t)

    # ------------------------------------------------------------------
    # Affichages
    # ------------------------------------------------------------------
    def afficher(self) -> None:
        """
        Affiche une représentation textuelle du réseau dans le terminal.
        Format simple mais lisible, suffisant pour les tests.
        """
        print("=== Reseau ===")
        print(f"Noeud d'entree : {self.noeud_entree}")
        print("Noeuds :")
        for nid in sorted(self.noeuds.keys()):
            print(f"  {nid} -> {self.noeuds[nid]}")
        print("Arcs :")
        for u, v in self.arcs:
            print(f"  {u} - {v}")

    def afficher_avec_terrain(self, t: Terrain) -> None:
        for ligne, l in enumerate(t.cases):
            for colonne, c in enumerate(l):
                if (ligne, colonne) not in self.noeuds.values():
                    if c == Case.OBSTACLE:
                        print("X", end="")
                    if c == Case.CLIENT:
                        print("C", end="")
                    if c == Case.VIDE:
                        print("~", end="")
                    if c == Case.ENTREE:
                        print("E", end="")
                    else:
                        print(" ", end="")
                else:
                    if c == Case.OBSTACLE:
                        print("T", end="")
                    if c == Case.CLIENT:
                        print("C", end="")
                    if c == Case.VIDE:
                        print("+", end="")
                    if c == Case.ENTREE:
                        print("E", end="")
                    else:
                        print(" ", end="")
            print()

    # ------------------------------------------------------------------
    # Calcul du coût du réseau
    # ------------------------------------------------------------------
    def calculer_cout(self, t: Terrain) -> float:
        cout = 0.0

        # 1,5 M€ par arc
        for _ in self.arcs:
            cout += 1.5

        # 1 M€ par noeud (2 M€ si sur un obstacle)
        for (i, j) in self.noeuds.values():
            if t[i][j] == Case.OBSTACLE:
                cout += 2.0
            else:
                cout += 1.0

        return cout
