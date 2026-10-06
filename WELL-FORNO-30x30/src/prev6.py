import sys, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from cad6 import draw_mpl, scaled_axes
from draw6 import plan, grid, PLAN_VIEW, north_arrow, section_marks
for fl in [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4]:
    R = plan(fl); grid(R, PLAN_VIEW)
    V = PLAN_VIEW
    fig = plt.figure(figsize=((V[2] - V[0]) / 100 / 25.4 + .2, (V[3] - V[1]) / 100 / 25.4 + .2))
    ax = scaled_axes(fig, 2, 2, V, 100)
    draw_mpl(ax, R, 100)
    fig.savefig('prev_F%d.png' % fl, dpi=95); plt.close(fig)
    print('ok', fl)
