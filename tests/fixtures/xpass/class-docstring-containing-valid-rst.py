class Youpi:
    """Dielectric profile calculation
    ==============================

    In the following example, we will show how to calculate the
    dielectric profiles as described in
    :ref:`dielectric-explanations`.

    Before producing trajectories to calculate dielectric profiles,
    you will need to consider which information you will need and thus
    need to print out. The dielectric profile calculators need
    unwrapped positions and charges of **all** charged atoms in the
    system. Unwrapped refers to the fact that you will need either
    "repaired" molecules (which in GROMACS ``trjconv`` with the ``-pbc
    mol`` option can do for you) or you will
    """
