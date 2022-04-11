import matplotlib.pyplot as plt

from matplotlib.transforms import offset_copy

cols = ['Column {}'.format(col) for col in range(1, 4)]

rows = ['Row {}'.format(row) for row in ['A', 'B', 'C', 'D']]

fig, axes = plt.subplots(nrows=4, ncols=3, figsize=(12, 8))

plt.setp(axes.flat, xlabel='X-label', ylabel='Y-label')

pad = 5 # in points

# for ax, col in zip(axes[0], cols):
#
#     ax.annotate(col, xy=(0.5, 1), xytext=(0, pad),
#
#                 xycoords='axes fraction', textcoords='offset points',
#
#                 size='large', ha='center', va='baseline')

# for ax, row in zip(axes[:,0], rows):
#
#     ax.annotate(row, xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - pad, 0),
#
#                 xycoords=ax.yaxis.label, textcoords='offset points',
#
#                 size='large', ha='right', va='center')

fig.tight_layout()

# tight_layout doesn't take these labels into account. We'll need

# to make some room. These numbers are are manually tweaked.

# You could automatically calculate them, but it's a pain.

fig.subplots_adjust(left=0.15, top=0.95)

plt.show()