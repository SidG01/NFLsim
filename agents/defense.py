# agents/defense.py
# ─────────────────────────────────────────────────────────────
# Defensive AI — picks a coverage shell each play and moves
# defenders according to that shell's rules each frame.
# ─────────────────────────────────────────────────────────────

import random
import math
import config

# Coverage shell probabilities — roughly realistic NFL distribution
COVERAGE_WEIGHTS = {
    "cover_0": 0.10,
    "cover_1": 0.30,
    "cover_2": 0.25,
    "cover_3": 0.20,
    "cover_4": 0.15,
}

# Numeric encoding for state vector
COVERAGE_ID = {
    "cover_0": 0,
    "cover_1": 1,
    "cover_2": 2,
    "cover_3": 3,
    "cover_4": 4,
}

class DefensiveAI:
    def __init__(self):
        self.coverage = None   # Current coverage shell string
        self.coverage_id = 0      # Numeric ID for state vector
        self.blitzers = []     # Players assigned to blitz this play

    def pick_coverage(self):
        """
        Randomly select a coverage shell weighted by NFL frequency.
        Called once per play before the snap.
        """
        shells = list(COVERAGE_WEIGHTS.keys())
        weights = list(COVERAGE_WEIGHTS.values())
        self.coverage = random.choices(shells, weights=weights)[0]
        self.coverage_id = COVERAGE_ID[self.coverage]
        self.blitzers = []
        return self.coverage

    def setup_coverage(self, offense, defense, scrimmage_y):
        """
        Position defenders according to the chosen coverage shell.
        Called once per play after pick_coverage().
        Sets each defender's target_x, target_y for the pre-snap alignment.
        """
        qb = next((p for p in offense if p.position == "QB"), None)
        wr = [p for p in offense if p.position == "WR"]
        te = next((p for p in offense if p.position == "TE"), None)
        rb = next((p for p in offense if p.position == "RB"), None)

        cbs = [p for p in defense if p.position == "CB"]
        safs = [p for p in defense if p.position == "S"]
        lbs = [p for p in defense if p.position == "LB"]
        dls = [p for p in defense if p.position == "DL"]

        field_cx = config.FIELD_WIDTH // 2

        # ── DL always rush the passer ──────────────────────────
        for i, dl in enumerate(dls):
            dl.target_x = field_cx + (i - 1.5) * 30
            dl.target_y = scrimmage_y - 10
            dl.coverage_type = "rush"

        # ── Coverage-specific assignments ──────────────────────
        if self.coverage == "cover_0":
            # All man, no safety help — CBs tight, safeties blitz
            self._assign_man_cbs(cbs, wr, tight=True)
            for saf in safs:
                saf.coverage_type = "blitz"
                saf.target_x = field_cx + random.randint(-60, 60)
                saf.target_y = scrimmage_y - 20
                self.blitzers.append(saf)
            for lb in lbs:
                lb.coverage_type = "blitz"
                lb.target_x = field_cx + random.randint(-80, 80)
                lb.target_y = scrimmage_y - 15
                self.blitzers.append(lb)

        elif self.coverage == "cover_1":
            # Man coverage, 1 deep safety, 1 safety blitzes
            self._assign_man_cbs(cbs, wr, tight=True)
            if len(safs) >= 2:
                # Free safety goes deep center
                safs[0].coverage_type = "deep_center"
                safs[0].target_x = field_cx
                safs[0].target_y = scrimmage_y - 120
                # Strong safety blitzes or covers TE
                if te:
                    safs[1].coverage_type = "man_te"
                    safs[1].target_x = te.x
                    safs[1].target_y = scrimmage_y - 20
                else:
                    safs[1].coverage_type = "blitz"
                    safs[1].target_x = field_cx
                    safs[1].target_y = scrimmage_y - 15
                    self.blitzers.append(safs[1])
            for lb in lbs:
                lb.coverage_type = "zone_under"
                lb.target_x = field_cx + random.randint(-100, 100)
                lb.target_y = scrimmage_y - 40

        elif self.coverage == "cover_2":
            # Zone — CBs hold flats, safeties split deep halves
            self._assign_zone_cbs(cbs, wr, scrimmage_y, depth=15)
            if len(safs) >= 2:
                safs[0].coverage_type = "deep_half_left"
                safs[0].target_x = field_cx - 160
                safs[0].target_y = scrimmage_y - 130
                safs[1].coverage_type = "deep_half_right"
                safs[1].target_x = field_cx + 160
                safs[1].target_y = scrimmage_y - 130
            for lb in lbs:
                lb.coverage_type = "zone_under"
                lb.target_x = field_cx + random.randint(-120, 120)
                lb.target_y = scrimmage_y - 40

        elif self.coverage == "cover_3":
            # Zone — 3 deep defenders, 4 underneath
            self._assign_zone_cbs(cbs, wr, scrimmage_y, depth=10)
            if len(safs) >= 2:
                safs[0].coverage_type = "deep_middle"
                safs[0].target_x = field_cx
                safs[0].target_y = scrimmage_y - 140
                safs[1].coverage_type = "deep_third_right"
                safs[1].target_x = field_cx + 180
                safs[1].target_y = scrimmage_y - 130
            for lb in lbs:
                lb.coverage_type = "zone_under"
                lb.target_x = field_cx + random.randint(-120, 120)
                lb.target_y = scrimmage_y - 45

        elif self.coverage == "cover_4":
            # Quarters — 4 deep defenders, very conservative
            self._assign_zone_cbs(cbs, wr, scrimmage_y, depth=8)
            if len(safs) >= 2:
                safs[0].coverage_type = "deep_quarter_left"
                safs[0].target_x = field_cx - 120
                safs[0].target_y = scrimmage_y - 150
                safs[1].coverage_type = "deep_quarter_right"
                safs[1].target_x = field_cx + 120
                safs[1].target_y = scrimmage_y - 150
            for lb in lbs:
                lb.coverage_type = "zone_under"
                lb.target_x = field_cx + random.randint(-100, 100)
                lb.target_y = scrimmage_y - 45

    def update_frame(self, offense, defense):
        """
        Called every frame during the play.
        Moves each defender according to their coverage assignment.
        """
        qb = next((p for p in offense if p.position == "QB"), None)
        wr = [p for p in offense if p.position == "WR"]
        te = next((p for p in offense if p.position == "TE"), None)
        rb = next((p for p in offense if p.position == "RB"), None)
        cbs = [p for p in defense if p.position == "CB"]

        for p in defense:
            ctype = getattr(p, 'coverage_type', None)

            if ctype == "rush":
                # DL — rush straight toward QB
                if qb:
                    p.target_x = qb.x
                    p.target_y = qb.y

            elif ctype == "man_wr1" and len(wr) > 0:
                p.target_x = wr[0].x
                p.target_y = wr[0].y

            elif ctype == "man_wr2" and len(wr) > 1:
                p.target_x = wr[1].x
                p.target_y = wr[1].y

            elif ctype == "man_wr3" and len(wr) > 2:
                p.target_x = wr[2].x
                p.target_y = wr[2].y

            elif ctype == "man_te" and te:
                p.target_x = te.x
                p.target_y = te.y

            elif ctype == "blitz":
                # Rush toward QB
                if qb:
                    p.target_x = qb.x
                    p.target_y = qb.y

            elif ctype in ("deep_center", "deep_middle",
                           "deep_half_left", "deep_half_right",
                           "deep_third_right", "deep_quarter_left",
                           "deep_quarter_right"):
                # Safeties drift to their zone — target already set in setup
                # Just let movement.py carry them there
                pass

            elif ctype == "zone_under":
                # LBs hold their zone — drift slightly toward nearest WR
                nearest = self._nearest_offensive_skill(p, offense)
                if nearest:
                    # Don't follow all the way — just drift slightly
                    dx = nearest.x - p.x
                    p.target_x = p.x + dx * 0.15
                # Hold depth
                pass

    def get_coverage_state(self):
        """
        Returns a one-hot encoded vector of the current coverage.
        Used as part of the agent's state input.
        [1,0,0,0,0] = Cover 0
        [0,1,0,0,0] = Cover 1  etc.
        """
        one_hot = [0.0] * 5
        one_hot[self.coverage_id] = 1.0
        return one_hot

    def _assign_man_cbs(self, cbs, wr, tight=False):
        """Assign CBs to wr in man coverage."""
        man_types = ["man_wr1", "man_wr2", "man_wr3"]
        for i, cb in enumerate(cbs):
            if i < len(wr):
                cb.coverage_type = man_types[i]
                cb.target_x = wr[i].x
                # Tight man = right on WR, loose man = 5 yards off
                offset = 5 if tight else 25
                cb.target_y = wr[i].y - offset

    def _assign_zone_cbs(self, cbs, wr, scrimmage_y, depth=15):
        """Assign CBs to flat zones in zone coverage."""
        zone_types = ["zone_flat_left", "zone_flat_right"]
        x_positions = [config.FIELD_WIDTH // 4,
                       3 * config.FIELD_WIDTH // 4]
        for i, cb in enumerate(cbs):
            cb.coverage_type = zone_types[i % 2]
            cb.target_x = x_positions[i % 2]
            cb.target_y = scrimmage_y - depth

    def _nearest_offensive_skill(self, defender, offense):
        """Find the nearest WR/TE/RB to a defender."""
        skill = [p for p in offense if p.position in ("WR", "TE", "RB")]
        if not skill:
            return None
        return min(skill, key=lambda p: math.sqrt(
            (p.x - defender.x)**2 + (p.y - defender.y)**2))