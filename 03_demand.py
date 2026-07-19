#!/usr/bin/env python3
"""
Genera demand_data.json realista per al mapa BCN.

Metodologia:
1. Graella censal Eurostat/GISCO 2021 (1 km): residents (T) i ocupats (EMP) per cel·la.
2. Refinament a subcel·les de 500 m repartint residents segons superfície
   d'edificis residencials OSM, i llocs de treball segons superfície
   d'oficines/comerç/indústria/equipaments OSM (escalats al total d'ocupats).
3. Model gravitatori doblement restringit (IPF) amb decaïment exponencial
   per generar els desplaçaments casa->feina (pops).
4. depot.DemandData: demanda especial (aeroport, universitats, hospitals...),
   càlcul de rutes de conducció (OSMnx) i consolidació.
"""
import os, json, glob, subprocess


def main():
    import numpy as np
    import geopandas as gpd
    import pandas as pd
    from shapely.geometry import box
    from scipy.spatial import cKDTree
    from scipy import sparse

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    import config_bcn as C

    DATA = "data"
    OUT = C.CITY_CODE
    os.makedirs(OUT, exist_ok=True)
    INITIAL = os.path.join(OUT, "demand_data.json")
    ROUTED = os.path.join(OUT, "demand_routed_checkpoint.json")

    # Punt de control: si ja tenim les rutes calculades, salta directament
    # a la consolidació (evita repetir 1,5 h de càlcul si un pas posterior falla)
    if os.path.exists(ROUTED):
        print("Trobat punt de control amb rutes: saltant generació i rutes.")
        from depot.demand import DemandData
        dd = DemandData(ROUTED, C.CITY_CODE, bbox=C.BBOX, outputdir=OUT)
        finalize(dd, C, OUT)
        return

    # ------------------------------------------------------------ 1. OSM urbà
    URBAN_PBF = f"{DATA}/bcn_urban.osm.pbf"
    URBAN_GJ = f"{DATA}/bcn_urban.geojson"
    if not os.path.exists(URBAN_GJ):
        bb = ",".join(map(str, C.BBOX))
        subprocess.run(["osmium", "extract", "-b", bb, "--overwrite",
                        "-o", f"{DATA}/bcn_bbox.osm.pbf", f"{DATA}/cataluna-latest.osm.pbf"],
                       check=True)
        subprocess.run(["osmium", "tags-filter", "--overwrite", "-o", URBAN_PBF,
                        f"{DATA}/bcn_bbox.osm.pbf",
                        "a/building", "a/landuse=industrial,commercial,retail",
                        "a/office", "a/shop",
                        "a/amenity=school,college,university,hospital"], check=True)
        subprocess.run(["osmium", "export", "--overwrite", "-o", URBAN_GJ, URBAN_PBF],
                       check=True)

    print("Llegint edificis/usos OSM...")
    urban = gpd.read_file(URBAN_GJ)
    urban = urban[urban.geometry.type.isin(["Polygon", "MultiPolygon"])].copy()
    urban = urban.to_crs(3035)
    urban["area"] = urban.geometry.area
    cent = urban.geometry.centroid
    urban["x"], urban["y"] = cent.x, cent.y

    def col(df, name):
        return df[name] if name in df.columns else pd.Series(None, index=df.index)

    b = col(urban, "building").fillna("")
    lu = col(urban, "landuse").fillna("")
    off = col(urban, "office").fillna("")
    shop = col(urban, "shop").fillna("")
    am = col(urban, "amenity").fillna("")

    RES_TYPES = {"residential", "apartments", "house", "detached", "terrace",
                 "semidetached_house", "dormitory", "bungalow", "yes"}
    urban["res_w"] = np.where(b.isin(RES_TYPES), urban["area"], 0.0)

    jw = np.zeros(len(urban))
    jw += np.where((off != "") | (b == "office"), urban["area"] * C.JOB_WEIGHTS["office"], 0)
    jw += np.where((shop != "") | (b == "retail"), urban["area"] * C.JOB_WEIGHTS["retail"], 0)
    jw += np.where((b == "commercial") | (lu == "commercial"), urban["area"] * C.JOB_WEIGHTS["commercial"], 0)
    jw += np.where((b.isin(["industrial", "warehouse"])) | (lu == "industrial"), urban["area"] * C.JOB_WEIGHTS["industrial"], 0)
    jw += np.where(am.isin(["school", "college", "university", "hospital"]), urban["area"] * C.JOB_WEIGHTS["civic"], 0)
    jw += np.where((jw == 0) & (b != "") & (~b.isin(RES_TYPES)), urban["area"] * C.JOB_WEIGHTS["other_building"], 0)
    urban["job_w"] = jw

    # --------------------------------------------------- 2. Graella censal
    print("Llegint la graella censal 2021...")
    gpkgs = glob.glob(f"{DATA}/grid2021/**/*.gpkg", recursive=True)
    assert gpkgs, "No s'ha trobat cap .gpkg dins data/grid2021/ (vegeu README)"
    bbox_3035 = gpd.GeoSeries([box(*C.BBOX)], crs=4326).to_crs(3035).total_bounds
    grid = gpd.read_file(gpkgs[0], bbox=tuple(bbox_3035))

    pop_col = next(c for c in ["T", "OBS_VALUE_T", "TOT_P", "POP"] if c in grid.columns)
    emp_col = next((c for c in ["EMP", "OBS_VALUE_EMP"] if c in grid.columns), None)
    grid[pop_col] = pd.to_numeric(grid[pop_col], errors="coerce").fillna(0).clip(lower=0)
    if emp_col:
        grid[emp_col] = pd.to_numeric(grid[emp_col], errors="coerce").fillna(0).clip(lower=0)
    else:
        grid["EMP_est"] = grid[pop_col] * 0.45
        emp_col = "EMP_est"
    grid = grid[grid[pop_col] + grid[emp_col] > 0].copy()
    EMP_RATIO = float(grid[emp_col].sum() / max(grid[pop_col].sum(), 1))
    print(f"  {len(grid)} cel·les, {int(grid[pop_col].sum()):,} residents, "
          f"{int(grid[emp_col].sum()):,} ocupats (ràtio {EMP_RATIO:.2f})")

    # ------------------------------- 3. Subcel·les de 500 m + repartiment
    print("Construint subcel·les...")
    S = C.SUBCELL_M
    sub_rows = []
    ux, uy = urban["x"].values, urban["y"].values
    res_w_all, job_w_all = urban["res_w"].values, urban["job_w"].values

    for _, cell in grid.iterrows():
        minx, miny, maxx, maxy = cell.geometry.bounds
        n = max(1, round((maxx - minx) / S))
        pop = float(cell[pop_col])
        subs = []
        for i in range(n):
            for j in range(n):
                x0, y0 = minx + i * S, miny + j * S
                mask = (ux >= x0) & (ux < x0 + S) & (uy >= y0) & (uy < y0 + S)
                subs.append((x0 + S / 2, y0 + S / 2,
                             res_w_all[mask].sum(), job_w_all[mask].sum()))
        rw = np.array([s[2] for s in subs])
        rw = rw / rw.sum() if rw.sum() > 0 else np.full(len(subs), 1 / len(subs))
        for k, s in enumerate(subs):
            # residents: cens de la cel·la repartit per superfície residencial OSM
            # job_w: pes laboral OSM cru (s'escala globalment després)
            sub_rows.append((s[0], s[1], pop * rw[k], s[3]))

    sub = pd.DataFrame(sub_rows, columns=["x", "y", "residents", "job_w"])
    # llocs de treball: pes laboral OSM, escalat perquè el total dins l'àrea
    # coincideixi amb els ocupats residents que es desplacen (sistema ~tancat)
    sub["jobs"] = sub["job_w"] * (sub["residents"].sum() * EMP_RATIO * C.COMMUTE_SHARE) / max(sub["job_w"].sum(), 1)
    sub = sub[sub["residents"] + sub["jobs"] >= C.MIN_POINT_ACTIVITY].reset_index(drop=True)
    pts_xy = sub[["x", "y"]].values
    sub_ll = gpd.GeoSeries(gpd.points_from_xy(sub.x, sub.y), crs=3035).to_crs(4326)
    sub["lon"], sub["lat"] = sub_ll.x.round(5), sub_ll.y.round(5)
    print(f"  {len(sub)} punts de demanda")

    # ----------------------------------- 4. Model gravitatori + pops
    print("Model gravitatori (IPF)...")
    O = sub["residents"].values * EMP_RATIO * C.COMMUTE_SHARE
    D = sub["jobs"].values
    D = D * (O.sum() / D.sum())

    tree = cKDTree(pts_xy)
    F = tree.sparse_distance_matrix(tree, C.MAX_COMMUTE_KM * 1000, output_type="coo_matrix")
    F.data = np.exp(-(F.data / 1000.0) / C.BETA_KM)
    F = F.tocsr() + sparse.identity(len(sub), format="csr")  # intrazonal

    # IPF: T_ij = a_i·O_i·b_j·D_j·F_ij
    #   a_i = 1/Σ_j(b_j·D_j·F_ij)   b_j = 1/Σ_i(a_i·O_i·F_ij)
    a = np.ones(len(sub)); bb_ = np.ones(len(sub))
    for _ in range(80):
        a = 1.0 / np.maximum(F.dot(bb_ * D), 1e-12)
        bb_ = 1.0 / np.maximum(F.T.dot(a * O), 1e-12)

    print("Mostrejant desplaçaments...")
    rng = np.random.default_rng(42)
    points, pops = [], []
    pid = {}

    def point_id(k):
        if k not in pid:
            pid[k] = f"dp_{k:05d}"
            points.append({"id": pid[k], "location": [float(sub.lon[k]), float(sub.lat[k])],
                           "jobs": 0, "residents": int(round(sub.residents[k])), "popIds": []})
        return pid[k]

    npop = 0
    for i in range(len(sub)):
        oi = O[i]
        if oi < 1:
            continue
        row = F.getrow(i)
        idx, vals = row.indices, row.data * a[i] * oi * bb_[row.indices] * D[row.indices]
        if vals.sum() <= 0:
            continue
        probs = vals / vals.sum()
        top = np.argsort(probs)[::-1][:12]  # limita destins/origen (control de pops)
        idx, probs = idx[top], probs[top] / probs[top].sum()
        alloc = rng.multinomial(int(round(oi)), probs)
        for j, wsize in zip(idx, alloc):
            if wsize < 8:
                continue
            hid, wid = point_id(i), point_id(int(j))
            while wsize > 0:
                s = int(min(wsize, C.POP_SIZE))
                pops.append({"id": f"pop_{npop:06d}", "size": s,
                             "residenceId": hid, "jobId": wid,
                             "drivingSeconds": 0, "drivingDistance": 0})
                npop += 1
                wsize -= s

    by_id = {p["id"]: p for p in points}
    for p in pops:
        by_id[p["jobId"]]["jobs"] += p["size"]
        by_id[p["residenceId"]]["popIds"].append(p["id"])

    print(f"  {len(points)} punts, {len(pops)} pops, "
          f"{sum(p['size'] for p in pops):,} desplaçaments")

    with open(INITIAL, "w") as f:
        json.dump({"points": points, "pops": pops}, f)

    # --------------------------------- 5. depot: especials + rutes
    print("depot.DemandData: demanda especial i rutes...")
    from depot.demand import DemandData

    dd = DemandData(INITIAL, C.CITY_CODE, bbox=C.BBOX, outputdir=OUT)

    for code, typ, name, loc, cap, psize, merge_w, maxd, res_split in C.SPECIAL_POINTS:
        np_ = {"type": typ, "name": name, "code": code, "location": loc,
               "total_capacity": cap, "pop_size": psize, "merge_within": merge_w}
        if maxd is not None:
            np_["max_distance"] = maxd
        if res_split is not None:
            np_["residential_split"] = res_split
        dd.add_points(np_)

    dd.enforce_max_pop_size(C.POP_SIZE)
    dd.save_schemas()
    dd.calculate_routes("osmnx", C.BBOX, max_workers=C.MAX_ROUTE_WORKERS)
    dd.save(ROUTED)  # punt de control: rutes desades
    finalize(dd, C, OUT)


def finalize(dd, C, OUT):
    dd.consolidate_pops()
    dd.merge_identical_commutes()
    dd.print_stats()
    dd.save(os.path.join(OUT, "demand_data.json"))
    dd.save_schemas()
    dd.create_config(C.MAP_NAME, bbox=C.BBOX, description=C.MAP_DESCRIPTION,
                     creator=C.CREATOR, version=C.VERSION, country=C.COUNTRY,
                     initial_view_state=C.INITIAL_VIEW)
    try:
        dd.create_description(C.CITY_CODE,
            methodology="Graella censal Eurostat 2021 refinada amb edificis OSM; "
                        "model gravitatori doblement restringit; rutes OSMnx.",
            data_sources="Eurostat/GISCO Census Grid 2021, OpenStreetMap (Geofabrik)")
    except Exception as e:
        # Bug conegut de depot amb popIds fusionats; el description.md és
        # opcional (només cal per publicar al registre)
        print(f"AVÍS: create_description ha fallat ({e}); es continua igualment.")
    print("\nDemanda generada a ./%s/demand_data.json" % OUT)


if __name__ == "__main__":
    # Imprescindible a macOS: multiprocessing usa 'spawn' i re-importa aquest
    # fitxer als processos fills; sense aquesta guarda ho re-executarien tot.
    main()
