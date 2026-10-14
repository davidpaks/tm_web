# Weboldalak készítése – feladatok

A tananyag böngészőben: **https://davidpaks.github.io/tm_web/**

Ott minden feladatnál megnyithatók a megoldások, és mappánként (Nyersanyag, Megoldás …) letölthetők `.zip`-ként.

## Hogyan működik

- A `Feladatok/<feladat neve>/<mappa>/` mappákban a fájlok **kicsomagolva** vannak.
- Minden `main`-re pusholás után a `.github/workflows/pages.yml` lefut: minden mappából `.zip`-et készít, legenerálja a főoldalt és a feladatonkénti oldalakat, majd publikálja a GitHub Pages-re.
- Új feladat: hozz létre egy új mappát a `Feladatok` alatt, benne pl. `Nyersanyag/` és `Megoldás/` almappával. Ha egy mappában van `index.html`, kap egy „Megnyitás böngészőben” gombot.
- Zip-et nem kell kézzel készíteni vagy feltölteni.
