========================
Software Selection spoke
========================

/installation/hub/software_selection/addon
==========================================
Handles software addons (*Additional software for Selected Environment*) selection.

Attributes:

* ``action`` - ``select`` or ``deselect``
* ``id`` - addon id (as defined in comps file) or glob pattern
* ``subselect`` (optional)
    * ``random`` - selects random subset of addons (``policy=just_check`` or
        ``policy=just_check_fail`` logically conflicts with ``subselect=random``,
        as it doesn't make sense to check a random selection).

/installation/hub/software_selection/environment
================================================
Handles *Base Environment* selection.

Attributes:

* ``id`` - environment id (as defined in comps file)
* ``select`` (optional) - ``random`` (random environment selection)
