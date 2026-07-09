# ──────────────────────────────────────────────────────────────────────────────
# _extract_data.py — throwaway generator: parse R3 Tcl source → model_data.json
#
# Source: models/BradleyCameron/R3_DesignSafeCI-Example/  (identical to
#         models/bradley2021_Building_system/ref/Input/R3_DesignSafeCI-Example_Input/)
#
# This script is committed for reproducibility — running it regenerates
# model_data.json byte-identically. It is NOT imported by model.py.
#
# Output schema (all raw imperial units: in, kip, ksi; conversion happens in
# model.py):
#   scalars       : dict of system parameters + node/element tag lists
#   nodes         : [[tag, x_in, y_in, mx, my, mz_or_None], ...]
#   fixities      : [[tag, c1, c2, c3], ...]
#   equalDOF      : [[master, slave, *dofs], ...]
#   materials     : [[type, tag, *args], ...]   (raw uniaxialMaterial tuples)
#   sections_hand : [{tag, kind, layers:[...], fibers:[...], agg:{...}}, ...]
#   sections_proc : [[shape, sID, mID, *dims], ...]   (Section W|HSS proc calls)
#   elements      : {type: [tuples, ...]}   keyed by element type
#   gravity_point : [[node, fx, fy, rz], ...]
#   gravity_ele   : [[w_kip_in, *ele_tags], ...]
#   pushover_loads: [[node, fx, fy, rz], ...]
# ──────────────────────────────────────────────────────────────────────────────
"""Parse the R3_DesignSafeCI-Example Tcl source into model_data.json."""
import json
import re
from pathlib import Path

SRC = Path(__file__).parent / "R3_DesignSafeCI-Example"
# Fall back to the canonical copy if the source isn't colocated here.
if not SRC.is_dir():
    SRC = (Path(__file__).parents[1] / "BradleyCameron" / "R3_DesignSafeCI-Example")
OUT = Path(__file__).parent / "model_data.json"

# Match a numeric token: integer, decimal, scientific notation, with optional
# leading sign. Accepts forms like 5e-04 (no decimal point) and +1.23e+04.
_NUM = r"[+-]?(?:\d+\.\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?|\d+(?:[eE][+-]?\d+)?)"
num_re = re.compile(_NUM)


def _read_lines(path):
    """Read a Tcl file, joining ``\\`` line-continuations into single logical lines."""
    raw = Path(path).read_text()
    # Join a trailing backslash (optionally followed by whitespace) with the
    # next line.
    raw = re.sub(r"\\\s*\n\s*", " ", raw)
    return raw.splitlines()


def _nums(s):
    """Return all numeric tokens in *s* as floats."""
    return [float(t) for t in num_re.findall(s)]


def _strip_comment(line):
    """Drop the trailing Tcl comment from *line*.

    Tcl comments start with ``#`` (line-leading) or ``;#`` (mid-line). We strip
    from the first ``#`` that is not inside a string — for this source the
    labels never contain ``#``, so a simple split is safe.
    """
    # The block opener ``{;`` must be preserved; only strip comments after a
    # genuine ``;#`` or a leading ``#``.
    if ";" in line and ";#" in line:
        return line[:line.find(";#")]
    return line


def _norm_ws(s):
    """Collapse runs of internal whitespace to single spaces and strip."""
    return " ".join(s.split())


# ── nodes ────────────────────────────────────────────────────────────────────
def parse_nodes():
    nodes = []
    for line in _read_lines(SRC / "B-Nodes.tcl"):
        s = line.strip()
        if not s.startswith("node"):
            continue
        toks = s.split()
        tag = int(toks[1])
        # _nums() includes the tag as its first value; drop it.
        vals = _nums(s)[1:]      # [x, y] or [x, y, mx, my, mz]
        x, y = vals[0], vals[1]
        if "-mass" in s and len(vals) >= 5:
            mx, my, mz = vals[2], vals[3], vals[4]
            nodes.append([tag, x, y, mx, my, mz])
        else:
            nodes.append([tag, x, y, None, None, None])
    return nodes


# ── materials ────────────────────────────────────────────────────────────────
def parse_materials():
    mats = []
    for line in _read_lines(SRC / "B-Materials.tcl"):
        s = _strip_comment(line).strip()
        if not s.startswith("uniaxialMaterial"):
            continue
        # tokens: uniaxialMaterial  <type>  <tag>  <args...>
        toks = s.split()
        mtype = toks[1]
        tag = int(float(toks[2]))
        args = []
        for t in toks[3:]:
            # keep flag tokens (-E0, -min, -max) as strings, numbers as floats
            if num_re.fullmatch(t):
                args.append(float(t))
            else:
                args.append(t)
        mats.append([mtype, tag, *args])
    return mats


# ── sections ─────────────────────────────────────────────────────────────────
def parse_sections():
    """Parse B-Sections.tcl into hand-built fiber sections + Section W|HSS calls.

    Hand-built sections use ``section Fiber <tag> {; ... };`` blocks where the
    body contains ``layer straight ...`` and ``fiber ...`` commands. The closing
    ``};`` sits at the end of the last body line. Proc-call sections
    (``Section W|HSS sID mID ...``) are single-line.
    """
    hand, proc = [], []
    lines = _read_lines(SRC / "B-Sections.tcl")

    i = 0
    while i < len(lines):
        s = _norm_ws(_strip_comment(lines[i]))

        # Section W|HSS proc call (single line)
        if s.startswith("Section"):
            toks = s.split()
            shape = toks[1]                      # "W" or "HSS"
            sid = int(float(toks[2]))
            mid = int(float(toks[3]))
            dims = []
            for t in toks[4:]:
                if num_re.fullmatch(t):
                    v = float(t)
                    dims.append(int(v) if v == int(v) else v)
            proc.append([shape, sid, mid, *dims])
            i += 1
            continue

        # section Fiber <tag> {; ...  (block opener — body is on following lines)
        if s.startswith("section Fiber"):
            tag = int(_nums(s)[0])
            layers, fibers = [], []
            j = i + 1
            # consume body lines until the closing brace
            while j < len(lines):
                bs = _norm_ws(_strip_comment(lines[j]))
                if "layer" in bs:
                    _parse_layer(bs, layers)
                if bs.startswith("fiber"):
                    _parse_fiber(bs, fibers)
                if "}" in lines[j]:
                    break
                j += 1
            hand.append({"tag": tag, "kind": "Fiber",
                         "layers": layers, "fibers": fibers})
            i = j + 1
            continue

        # section Aggregator <tag> <mat> Vy -section <sec>
        if s.startswith("section Aggregator"):
            toks = s.split()
            tag = int(float(toks[2]))
            mat = int(float(toks[3]))
            dof = toks[4]                          # "Vy"
            sub = int(float(toks[toks.index("-section") + 1]))
            for h in reversed(hand):
                if h["tag"] == sub:
                    h["aggregator"] = {"tag": tag, "mat": mat, "dof": dof}
                    break
            i += 1
            continue
        i += 1
    return hand, proc


def _parse_layer(bs, layers):
    """Append a ``layer straight`` entry from line *bs* to *layers*."""
    if "straight" not in bs:
        return
    nums = _nums(bs)
    if len(nums) < 7:
        return
    # layer straight <mat> <n> <area> <yI> <zI> <yJ> <zJ>
    mat = int(nums[0]); n = int(nums[1]); area = nums[2]
    layers.append({"kind": "straight", "mat": mat, "n": n, "area": area,
                   "yI": nums[3], "zI": nums[4], "yJ": nums[5], "zJ": nums[6]})


def _parse_fiber(bs, fibers):
    """Append a ``fiber`` entry from line *bs* to *fibers*.

    Format: ``fiber <y> <z> <area> <mat>`` — but the Tcl uses tab-aligned sparse
    columns, so we just grab all numerics in order.
    """
    nums = _nums(bs)
    if len(nums) < 4:
        return
    fibers.append({"y": nums[0], "z": nums[1],
                   "area": nums[2], "mat": int(nums[3])})


# ── elements ─────────────────────────────────────────────────────────────────
def _parse_list_literal(s):
    """Parse a Tcl ``[list a b c ...]`` body (the substring inside the brackets)
    into a list of ints (if all integer) else floats/strings."""
    out = []
    for t in s.split():
        if num_re.fullmatch(t):
            v = float(t)
            out.append(int(v) if v == int(v) else v)
        else:
            out.append(t)
    return out


def parse_elements():
    """Parse B-Elements.tcl.

    Two forms:
      (1) ``DefineElements "<type>" $eT $iN $jN <args...>``  — batch helper
      (2) ``element <type> <tag> <i> <j> <args...>``         — single line

    The lists ($eT/$iN/$jN/$mT/$sT) are assigned on SEPARATE preceding lines via
    ``set <var> [list ...]``, then referenced by the DefineElements call. We
    track those assignments as state and resolve the $refs.

    The DefineElements helper auto-adds equalDOF constraints for the
    zeroLength-IMK / -SBL / -SBR variants; we surface those as a separate
    ``auto_equalDOF`` list so model.py can apply them.
    """
    elements = {
        "dispBeamColumn": [],
        "elasticBeamColumn": [],
        "truss": [],
        "zeroLength_IMK": [],
        "zeroLength_SBL": [],
        "zeroLength_SBR": [],
        "zeroLength_weld": [],
        "zeroLengthSection": [],
    }
    auto_eqdof = []          # auto-generated by DefineElements variants
    var_lists = {}           # name -> list of int/float (the Tcl list literals)

    for raw in _read_lines(SRC / "B-Elements.tcl"):
        s = _strip_comment(raw).strip()
        if not s:
            continue

        # ── track ``set <var> [list ...]`` assignments ──
        m = re.match(r"set\s+(\w+)\s+\[list\s+([^\]]*)\]", s)
        if m:
            var_lists[m.group(1)] = _parse_list_literal(m.group(2))
            continue

        # ── DefineElements "<type>" $eT $iN $jN <args> ──
        if s.startswith("DefineElements"):
            etype = s.split('"')[1]
            after_quote = s.split('"', 2)[2].strip()
            tokens = after_quote.split()
            # Walk tokens in document order. $var refs fill eT, iN, jN, then
            # the 4th ref (mT or sT). Literals are collected in order.
            ref_vals = []          # resolved ref lists, in order of appearance
            literals = []          # literal tokens, in order of appearance
            for tok in tokens:
                if tok.startswith("$"):
                    ref_vals.append(var_lists.get(tok[1:]))
                else:
                    if num_re.fullmatch(tok):
                        v = float(tok)
                        literals.append(int(v) if v == int(v) else v)
                    else:
                        literals.append(tok)
            if len(ref_vals) < 3:
                continue
            et, in_, jn = ref_vals[0], ref_vals[1], ref_vals[2]
            fourth = ref_vals[3] if len(ref_vals) >= 4 else None
            n = len(et)
            for k in range(n):
                args = _build_batch_args(etype, literals, fourth, fourth, k)
                _add_batch_element(elements, auto_eqdof, etype,
                                   et[k], in_[k], jn[k], args)
            continue

        # ── single ``element <type> ...`` line ──
        if s.startswith("element"):
            toks = s.split()
            etype = toks[1]
            tag = int(float(toks[2]))
            ni = int(float(toks[3]))
            nj = int(float(toks[4]))
            rest = toks[5:]
            _add_single_element(elements, tag, ni, nj, etype, rest)

    return elements, auto_eqdof


def refs_count(s):
    """Unused placeholder kept for clarity; refs are counted inline now."""
    return len(re.findall(r"\$(\w+)", s))


def _build_batch_args(etype, literals, sT_list, mT_list, k):
    """Build the per-element args tuple for a DefineElements batch call.

    *literals* is the ordered list of non-$var tokens on the DefineElements line
    (numbers and flags), in the order they appear. *sT_list*/*mT_list* are the
    resolved per-element values for the 4th $var (only one is relevant per type).
    """
    if etype == "dispBeamColumn":
        # signature: $eT $iN $jN <nIP> $sT <transf>
        # literals = [nIP, transf]; sT_list[k] = secTag
        n_ip = literals[0]
        transf = literals[1]
        sec = sT_list[k] if sT_list else None
        return [n_ip, sec, transf]
    if etype in ("zeroLength-IMK", "zeroLength-SBL", "zeroLength-SBR"):
        # signature: $eT $iN $jN -mat $mT -dir <dir>
        # literals = ["-mat", "-dir", dir]
        direction = literals[literals.index("-dir") + 1]
        mat = mT_list[k] if mT_list else None
        return ["-mat", mat, "-dir", direction]
    if etype == "zeroLengthSection":
        # signature: $eT $iN $jN <secTag> -orient <6v> -doRayleigh <n>
        # literals = [secTag, "-orient", 1,0,0, 0,1,0, "-doRayleigh", 0]
        return literals
    return literals


def _add_batch_element(elements, auto_eqdof, etype, tag, ni, nj, args):
    """Dispatch one element created via the DefineElements helper."""
    if etype == "dispBeamColumn":
        # args = [nIP, secTag, transfTag]
        n_ip, sec, transf = int(args[0]), int(args[1]), int(args[2])
        elements["dispBeamColumn"].append([tag, ni, nj, n_ip, sec, transf])
    elif etype == "elasticBeamColumn":
        # args = [A, E, Iz, transf]
        A, E, Iz, transf = args[0], args[1], args[2], int(args[3])
        elements["elasticBeamColumn"].append([tag, ni, nj, A, E, Iz, transf])
    elif etype == "truss":
        # args = [A, matTag]
        A, mat = args[0], int(args[1])
        elements["truss"].append([tag, ni, nj, A, mat])
    elif etype in ("zeroLength-IMK", "zeroLength-SBL", "zeroLength-SBR"):
        # args = ["-mat", matTag, "-dir", dir]
        mat = int(args[args.index("-mat") + 1])
        direction = int(args[args.index("-dir") + 1])
        key = "zeroLength_" + etype.split("-")[1]   # IMK / SBL / SBR
        elements[key].append([tag, ni, nj, mat, direction])
        # auto equalDOF rules (from P-DefineElements.tcl)
        if etype == "zeroLength-IMK":
            auto_eqdof.append([ni, nj, 1, 2])
        elif etype == "zeroLength-SBL":
            auto_eqdof.append([ni, nj - 1, 2, 3])
        elif etype == "zeroLength-SBR":
            auto_eqdof.append([ni + 1, nj, 2, 3])
    elif etype == "zeroLengthSection":
        # DefineElements "zeroLengthSection" $eT $iN $jN <secTag> -orient <6v> -doRayleigh <n>
        sec = int(args[0])
        orient = None
        do_rayleigh = 0
        if "-orient" in args:
            o = args.index("-orient")
            orient = [float(t) for t in args[o + 1:o + 7]]
        if "-doRayleigh" in args:
            do_rayleigh = int(args[args.index("-doRayleigh") + 1])
        elements["zeroLengthSection"].append(
            [tag, ni, nj, sec, orient, do_rayleigh])
    else:
        # Unknown batch type — record as a zeroLength with raw args
        elements.setdefault("_other", []).append([etype, tag, ni, nj, args])


def _add_single_element(elements, tag, ni, nj, etype, rest):
    """Dispatch one ``element <type> ...`` single line."""
    if etype == "elasticBeamColumn":
        A, E, Iz = float(rest[0]), float(rest[1]), float(rest[2])
        transf = int(float(rest[3]))
        elements["elasticBeamColumn"].append([tag, ni, nj, A, E, Iz, transf])
    elif etype == "zeroLengthSection":
        # element zeroLengthSection <tag> <i> <j> <sec> -orient ... -doRayleigh 0
        sec = int(float(rest[0]))
        orient = None
        do_rayleigh = 0
        if "-orient" in rest:
            o = rest.index("-orient")
            orient = [float(t) for t in rest[o + 1:o + 7]]
        if "-doRayleigh" in rest:
            do_rayleigh = int(float(rest[rest.index("-doRayleigh") + 1]))
        elements["zeroLengthSection"].append(
            [tag, ni, nj, sec, orient, do_rayleigh])
    elif etype == "zeroLength":
        # weld elements: -mat m1 m2 m3 -dir 1 2 6 -orient x1 y1 z1 x2 y2 z2
        mats, dirs, orient = [], [], None
        if "-mat" in rest:
            mi = rest.index("-mat")
            # collect until next -dir / -orient
            j = mi + 1
            while j < len(rest) and not rest[j].startswith("-"):
                mats.append(int(float(rest[j]))); j += 1
        if "-dir" in rest:
            di = rest.index("-dir")
            j = di + 1
            while j < len(rest) and not rest[j].startswith("-"):
                dirs.append(int(float(rest[j]))); j += 1
        if "-orient" in rest:
            oi = rest.index("-orient")
            orient = [float(t) for t in rest[oi + 1:oi + 7]]
        elements["zeroLength_weld"].append([tag, ni, nj, mats, dirs, orient])
    else:
        elements.setdefault("_other", []).append(
            [etype, tag, ni, nj, rest])


# ── constraints ──────────────────────────────────────────────────────────────
def parse_constraints():
    fixities, equalDOF = [], []
    text = (SRC / "B-Constraints.tcl").read_text()
    for line in text.splitlines():
        s = _strip_comment(line).strip()
        if s.startswith("fix"):
            toks = s.split()
            fixities.append([int(float(toks[1])),
                             int(float(toks[2])),
                             int(float(toks[3])),
                             int(float(toks[4]))])
        elif s.startswith("equalDOF"):
            nums = _nums(s)
            equalDOF.append([int(nums[0]), int(nums[1])] +
                            [int(n) for n in nums[2:]])
    return fixities, equalDOF


# ── loads ────────────────────────────────────────────────────────────────────
def parse_gravity_loads():
    point, ele = [], []
    text = (SRC / "B-GravityLoads.tcl").read_text()
    in_pattern = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("pattern Plain"):
            in_pattern = True
            continue
        if in_pattern and s.startswith("}"):
            break
        if not in_pattern:
            continue
        bs = _strip_comment(s).strip()
        if bs.startswith("load"):
            nums = _nums(bs)
            point.append([int(nums[0]), nums[1], nums[2], nums[3]])
        elif bs.startswith("eleLoad"):
            # Format: eleLoad -ele <tags...> -type -beamUniform <w>
            # The load value <w> is the LAST numeric token; element tags precede it.
            nums = _nums(bs)
            w = nums[-1]                       # beamUniform load value
            eles = [int(n) for n in nums[:-1]]
            ele.append([w, *eles])
    return point, ele


def parse_pushover_loads():
    text = (SRC / "B-PushoverLoads.tcl").read_text()
    # lat1/lat2/lat3 are set as Tcl vars then used in the pattern
    lat1 = lat2 = lat3 = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("set lat1"):
            lat1 = _nums(s)[0]
        elif s.startswith("set lat2"):
            lat2 = _nums(s)[0]
        elif s.startswith("set lat3"):
            lat3 = _nums(s)[0]
    loads = [[44, lat1, 0.0, 0.0], [49, lat2, 0.0, 0.0], [54, lat3, 0.0, 0.0],
             [60, lat1, 0.0, 0.0], [65, lat2, 0.0, 0.0], [70, lat3, 0.0, 0.0]]
    return {"lat1": lat1, "lat2": lat2, "lat3": lat3, "loads": loads}


# ── scalars / info files ─────────────────────────────────────────────────────
def parse_scalars():
    sp = (SRC / "B-SystemParameters.tcl").read_text()
    height = _nums([l for l in sp.splitlines() if "set height" in l][0])[0]
    stories = int(_nums([l for l in sp.splitlines() if "set stories" in l][0])[0])
    zeta = _nums([l for l in sp.splitlines() if "set zeta" in l][0])[0]
    n_mod = _nums([l for l in sp.splitlines() if l.strip().startswith("set n")][0])[0]

    # cyclic drift targets (B-CyclicDriftTargets.tcl)
    cyc_path = SRC / "BuildingAnalysis" / "B-CyclicDriftTargets.tcl"
    cyclic_targets = _nums(cyc_path.read_text()) if cyc_path.is_file() else []

    # weld info (B-WeldInfo.tcl) — capacities + element/node lists
    weld_path = SRC / "B-WeldInfo.tcl"
    weld = {}
    if weld_path.is_file():
        wt = weld_path.read_text()
        weld["weld_eles"] = [int(x) for x in
                             re.search(r"WeldEles\s*\[list\s+([^\]]*)\]", wt).group(1).split()]
        weld["i_nodes"] = [int(x) for x in
                           re.search(r"iNodes\s*\[list\s+([^\]]*)\]", wt).group(1).split()]
        weld["j_nodes"] = [int(x) for x in
                           re.search(r"jNodes\s*\[list\s+([^\]]*)\]", wt).group(1).split()]
        weld["weld_mat"] = [int(x) for x in
                            re.search(r"WeldMat\s*\[list\s+([^\]]*)\]", wt).group(1).split()]
        weld["stories"] = [int(x) for x in
                           re.search(r"WeldStories\s*\[list\s+([^\]]*)\]", wt).group(1).split()]
        # capacities from the expr abs(BRn)/(<cap>*1.00)
        caps = re.findall(r"/\(([\d.eE+-]+)\*1\.00\)", wt)
        weld["capacities_kip"] = [float(c) for c in caps]
        # the rigid EBC elements connected to each weld = WeldEle - 1
        weld["ebc_eles"] = [e - 1 for e in weld["weld_eles"]]

    return {
        "height_in": height,
        "stories": stories,
        "story_heights_in": [180.0] * stories,
        "zeta": zeta,
        "n_mod": n_mod,
        "control_node": 54,
        "control_dof": 1,
        "drift_nodes": [39, 44, 49, 54],          # base + 3 floor levels (col D)
        "base_nodes": [1, 25, 39, 55, 71, 85, 109, 133, 157, 171, 185, 209,
                       233, 247, 261, 285, 309, 323],
        "brace_end_nodes_1": [813, 824, 835, 846, 857, 868],
        "brace_end_nodes_2": [821, 832, 843, 854, 865, 876],
        "cyclic_drift_targets": cyclic_targets,
        "drift_max": 0.10,
        "pushover_dx_in": 0.02,
        "weld": weld,
    }


def main():
    nodes = parse_nodes()
    materials = parse_materials()
    sections_hand, sections_proc = parse_sections()
    elements, auto_eqdof = parse_elements()
    fixities, equalDOF = parse_constraints()
    grav_point, grav_ele = parse_gravity_loads()
    pushover = parse_pushover_loads()
    scalars = parse_scalars()

    data = {
        "scalars": scalars,
        "nodes": nodes,
        "fixities": fixities,
        "equalDOF": equalDOF,
        "auto_equalDOF": auto_eqdof,
        "materials": materials,
        "sections_hand": sections_hand,
        "sections_proc": sections_proc,
        "elements": elements,
        "gravity_point": grav_point,
        "gravity_ele": grav_ele,
        "pushover": pushover,
    }
    OUT.write_text(json.dumps(data, indent=2))

    # ── summary ──
    n_ele = sum(len(v) for k, v in elements.items() if k != "_other")
    print(f"nodes          : {len(nodes):4d}  (tags {nodes[0][0]}..{nodes[-1][0]})")
    print(f"materials      : {len(materials):4d}  (tags {materials[0][1]}.."
          f"{materials[-1][1]})")
    print(f"sections hand  : {len(sections_hand):4d}")
    print(f"sections proc  : {len(sections_proc):4d}")
    print(f"elements total : {n_ele:4d}")
    for k, v in elements.items():
        if v:
            print(f"  {k:20s}: {len(v):4d}")
    print(f"fixities       : {len(fixities):4d}")
    print(f"equalDOF expl. : {len(equalDOF):4d}")
    print(f"equalDOF auto  : {len(auto_eqdof):4d}")
    print(f"gravity point  : {len(grav_point):4d}")
    print(f"gravity ele-grp: {len(grav_ele):4d}")
    print(f"pushover loads : {len(pushover['loads'])}")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
