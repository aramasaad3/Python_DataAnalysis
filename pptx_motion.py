"""
Slide transitions and entrance animations for python-pptx.

python-pptx has no API for animations, so this module writes the PowerPoint XML
(<p:transition> and <p:timing>) directly into each slide.

    set_transition(slide, "morph")                 # morph, fade, push_up, push_left, split, zoom
    animate(slide, [(shape, "rise"), (textbox, "rise", True)])   # True = one paragraph at a time

All animations start automatically after the transition, one after another
("With previous" + a small delay each), so the presenter only clicks to change slide.
"""
from itertools import count

from lxml import etree

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P14 = "http://schemas.microsoft.com/office/powerpoint/2010/main"
P159 = "http://schemas.microsoft.com/office/powerpoint/2015/09/main"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
NS = f'xmlns:p="{P}" xmlns:a="{A}"'

_SIMPLE = {
    "fade": "<p:fade/>",
    "push_up": '<p:push dir="u"/>',
    "push_left": '<p:push dir="l"/>',
    "split": '<p:split orient="vert" dir="out"/>',
    "zoom": '<p:zoom dir="in"/>',
}


def _insert_after_header(slide, node):
    """Transition and timing must come right after <p:clrMapOvr>, in that order."""
    el = slide._element
    anchor = el.find(f"{{{P}}}clrMapOvr")
    for tag in (f"{{{MC}}}AlternateContent", f"{{{P}}}transition"):
        found = el.find(tag)
        if found is not None and node.tag.endswith("timing"):
            anchor = found
    anchor.addnext(node)


def set_transition(slide, kind="fade", speed="med"):
    if kind == "morph":   # PowerPoint 2019/365 Morph, with a Fade fallback for older versions
        xml = (f'<mc:AlternateContent xmlns:mc="{MC}">'
               f'<mc:Choice xmlns:p159="{P159}" Requires="p159">'
               f'<p:transition {NS} xmlns:p14="{P14}" spd="slow" p14:dur="1100"><p159:morph option="byObject"/>'
               f'</p:transition></mc:Choice>'
               f'<mc:Fallback><p:transition {NS} spd="slow"><p:fade/></p:transition></mc:Fallback>'
               f'</mc:AlternateContent>')
    else:
        xml = f'<p:transition {NS} spd="{speed}">{_SIMPLE[kind]}</p:transition>'
    _insert_after_header(slide, etree.fromstring(xml))


def _target(spid, para):
    if para is None:
        return f'<p:spTgt spid="{spid}"/>'
    return f'<p:spTgt spid="{spid}"><p:txEl><p:pRg st="{para}" end="{para}"/></p:txEl></p:spTgt>'


def _effect(kind, tgt, ids, dur):
    """Returns (presetID, presetSubtype, behaviour XML) for one entrance effect."""
    def bhvr(extra=""):
        return f'<p:cBhvr{extra}><p:cTn id="{next(ids)}" dur="{dur}" fill="hold"/><p:tgtEl>{tgt}</p:tgtEl>'

    show = (f'<p:set><p:cBhvr><p:cTn id="{next(ids)}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/>'
            f'</p:stCondLst></p:cTn><p:tgtEl>{tgt}</p:tgtEl><p:attrNameLst><p:attrName>style.visibility'
            f'</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>')

    def filt(name):
        return (f'<p:animEffect transition="in" filter="{name}"><p:cBhvr><p:cTn id="{next(ids)}" dur="{dur}"/>'
                f'<p:tgtEl>{tgt}</p:tgtEl></p:cBhvr></p:animEffect>')

    additive = ' additive="base"'

    def move(attr, start, end, val="strVal"):
        return (f'<p:anim calcmode="lin" valueType="num">{bhvr(additive)}<p:attrNameLst><p:attrName>'
                f'{attr}</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst><p:tav tm="0"><p:val><p:{val} val="{start}"/>'
                f'</p:val></p:tav><p:tav tm="100000"><p:val><p:strVal val="{end}"/></p:val></p:tav></p:tavLst></p:anim>')

    if kind == "fade":
        return 10, 0, show + filt("fade")
    if kind == "rise":    # "Float in": fade in while moving up a little
        return 42, 0, show + filt("fade") + move("ppt_x", "#ppt_x", "#ppt_x") + move("ppt_y", "#ppt_y+.06", "#ppt_y")
    if kind == "wipe":    # reveal from the left
        return 22, 8, show + filt("wipe(left)")
    if kind == "zoom":    # grow from the centre
        return 53, 16, show + move("ppt_w", "0", "#ppt_w", "fltVal") + move("ppt_h", "0", "#ppt_h", "fltVal") + filt("fade")
    raise ValueError(kind)


def animate(slide, items, start=250, step=280, dur=550):
    """items: (shape, kind) or (shape, kind, by_paragraph). Plays automatically in order."""
    ids = count(5)
    effects, builds = [], []
    t = start
    for item in items:
        shape, kind = item[0], item[1]
        by_para = len(item) > 2 and item[2]
        paras = [None]
        if by_para:
            paras = [i for i, p in enumerate(shape.text_frame.paragraphs) if p.text.strip()]
        for para in paras:
            node_id = next(ids)
            preset, sub, behaviour = _effect(kind, _target(shape.shape_id, para), ids, dur)
            node_type = "afterEffect" if not effects else "withEffect"
            effects.append(
                f'<p:par><p:cTn id="{node_id}" presetID="{preset}" presetClass="entr" presetSubtype="{sub}" '
                f'fill="hold" grpId="0" nodeType="{node_type}"><p:stCondLst><p:cond delay="{t}"/></p:stCondLst>'
                f'<p:childTnLst>{behaviour}</p:childTnLst></p:cTn></p:par>')
            t += step
        if shape._element.tag == f"{{{P}}}sp":           # text shapes need a build entry
            builds.append(f'<p:bldP spid="{shape.shape_id}" grpId="0"' +
                          (' build="p"/>' if by_para else ' animBg="1"/>'))
    if not effects:
        return
    xml = (f'<p:timing {NS}><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
           f'<p:childTnLst><p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq">'
           f'<p:childTnLst><p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/>'
           f'<p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
           f'<p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
           + "".join(effects) +
           f'</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
           f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
           f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
           f'</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>'
           + (f'<p:bldLst>{"".join(builds)}</p:bldLst>' if builds else "") +
           '</p:timing>')
    _insert_after_header(slide, etree.fromstring(xml))
