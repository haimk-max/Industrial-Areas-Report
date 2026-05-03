# Phase 0c QA Report — Parameters Dictionary

- Total parameters: 183
- With drinking water standard: 101
- Calculated/excluded: 2 (BETK, TPFAS)
- Families: 15

## Family breakdown

| Family | Count | Codes (first 10) |
|--------|-------|-----------------|
| CVOC | 38 | CCL4, CDCE, CHLET, CHLMT, CTN2, CTN4, DCB13, DCDFM, DCET, DCET1... |
| pesticides | 32 | 24DNT, 26DNT, ADRN, ALAC, ALCB, ALDSU, ALSD, ATRA, BRMC, CARFN... |
| heavy_metals | 23 | AG, AL, AS, BA, BE, CD, CO, CR, CU, FE... |
| BTEX | 17 | BENZ, BRBNZ, ETBN, IPBNZ, NAPT, NBTBZ, NPBNZ, OXYL, PTOLU, PXYL... |
| physical | 15 | COLR, DO, EC, ECFD, HARD, MBAS, ORP, PHFD, PHLB, T... |
| major_ions | 12 | B, BR, CA, CL, F, HCO3, K, Mg, NA, NO3... |
| PFAS_A | 11 | ADONA, PFBA, PFDA, PFDoA, PFESA, PFHpA, PFHxA, PFNA, PFOA, PFPeA... |
| PFAS_S | 8 | 6:2FT, 82FTS, FOSA, PFBS, PFDS, PFHpS, PFHxS, PFOS |
| THM | 6 | BRDCM, CHLF, DBRMT, DCBM, TRBRM, CF |
| emerging | 5 | ACET, BEPT, BNZP, CARBO, FORM |
| other_halogenated | 5 | BRCM, BRMET, DBR12, DBRM, ETDB |
| fuel | 4 | MOL, MTBE, TOC, TPH |
| radioactivity | 3 | ALFA, BETA, BETK |
| nitrogenous | 3 | CN, TN-N, TP-P |
| PFAS | 1 | TPFAS |

## Validation
- TPFAS is_calculated=True: ✅
- All PFAS species listed: ✅
- PFAS_S group (sulfonate): 6:2FT, 82FTS, FOSA, PFBS, PFDS, PFHpS, PFHxS, PFOS
- PFAS_A group (carboxylate): ADONA, PFBA, PFDA, PFDoA, PFESA, PFHpA, PFHxA, PFNA, PFOA, PFPeA, PFUnA