"""
Line icons (24 x 24, stroke style) for the presentation slides.
Slides:  icon_png() draws them with matplotlib into transparent PNG files.
"""
import os
import re

ICONS = {
    "gamepad": '<path d="M6 12h4M8 10v4"/><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M15 11h.01M18 11h.01"/>',
    "controller": '<path d="M6 12h4M8 10v4"/><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="15" cy="11" r="1"/><circle cx="18" cy="11" r="1"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "tag": '<path d="M12 2H2v10l9.17 9.17a2 2 0 0 0 2.83 0l7.17-7.17a2 2 0 0 0 0-2.83L12 2z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    "check": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "chart": '<path d="M3 3v18h18"/><path d="M18 17V9M13 17V5M8 17v-3"/>',
    "database": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/>',
    "wrench": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "layers": '<path d="M12 2 2 7l10 5 10-5-10-5z"/><path d="m2 17 10 5 10-5M2 12l10 5 10-5"/>',
    "bulb": '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6M10 22h4"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/>',
    "monitor": '<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    "star": '<path d="m12 2 3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>',
    "dollar": '<path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
    "trending": '<path d="m22 7-8.5 8.5-5-5L2 17"/><path d="M16 7h6v6"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20M2 12h20"/>',
    "sliders": '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
    "route": '<circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/>',
}


def icon_png(name, color="#1d2433", size=256, folder="presentation/img/icons", stroke=1.8):
    """Draw one icon with matplotlib and save it as a transparent PNG. Returns the file path."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Ellipse, FancyBboxPatch, PathPatch
    from svgpath2mpl import parse_path

    os.makedirs(folder, exist_ok=True)
    path = f"{folder}/{name}_{color.strip('#')}.png"
    if os.path.exists(path):
        return path
    dpi = 100
    fig = plt.figure(figsize=(size / dpi, size / dpi), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-1, 25)
    ax.set_ylim(25, -1)                       # SVG y axis points down
    ax.axis("off")
    lw = size / 26 * stroke * 72 / dpi
    style = dict(fill=False, edgecolor=color, linewidth=lw, capstyle="round", joinstyle="round")
    svg = ICONS[name]
    for d in re.findall(r'<path d="([^"]+)"', svg):
        ax.add_patch(PathPatch(parse_path(d), **style))
    for cx, cy, r in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"', svg):
        ax.add_patch(Circle((float(cx), float(cy)), float(r), **style))
    for cx, cy, rx, ry in re.findall(r'<ellipse cx="([\d.]+)" cy="([\d.]+)" rx="([\d.]+)" ry="([\d.]+)"', svg):
        ax.add_patch(Ellipse((float(cx), float(cy)), 2 * float(rx), 2 * float(ry), **style))
    for x, y, w, h, rx in re.findall(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" rx="([\d.]+)"', svg):
        ax.add_patch(FancyBboxPatch((float(x), float(y)), float(w), float(h),
                                    boxstyle=f"round,pad=0,rounding_size={rx}", **style))
    fig.savefig(path, transparent=True, dpi=dpi)
    plt.close(fig)
    return path
