#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# NeuORC v1.1 - Web Interface
# Necmettin Erbakan University Organic Rankine Cycle Calculator
#
import os
import sys
import json
import base64
import io
from math import log, log10

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import CoolProp
import CoolProp.CoolProp as CP
from CoolProp.Plots import StateContainer, PropertyPlot
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


# Load custom refrigerant R1336mzz(E) if available
json_path = resource_path('R1336mzz(E).json')
try:
    with open(json_path, 'r') as file:
        R1336mzze = json.load(file)
    CP.add_fluids_as_JSON("HEOS", json.dumps(R1336mzze))
except FileNotFoundError:
    pass


FLUIDS = [
    "1-Butene", "Acetone", "Air", "Ammonia", "Argon", "Benzene",
    "CarbonDioxide", "CarbonMonoxide", "CarbonylSulfide", "CycloHexane",
    "CycloPropane", "Cyclopentane", "D4", "D5", "D6", "Deuterium",
    "Dichloroethane", "DiethylEther", "DimethylCarbonate", "DimethylEther",
    "Ethane", "Ethanol", "EthylBenzene", "Ethylene", "EthyleneOxide",
    "Fluorine", "HFE143m", "HeavyWater", "Helium", "Hydrogen",
    "HydrogenChloride", "HydrogenSulfide", "IsoButane", "IsoButene",
    "Isohexane", "Isopentane", "Krypton", "MD2M", "MD3M", "MD4M", "MDM",
    "MM", "Methane", "Methanol", "MethylLinoleate", "MethylLinolenate",
    "MethylOleate", "MethylPalmitate", "MethylStearate", "Neon", "Neopentane",
    "Nitrogen", "NitrousOxide", "Novec649", "OrthoDeuterium", "OrthoHydrogen",
    "Oxygen", "ParaDeuterium", "ParaHydrogen", "Propylene", "Propyne",
    "R11", "R113", "R114", "R115", "R116", "R12", "R123", "R1233zd(E)",
    "R1234yf", "R1234ze(E)", "R1234ze(Z)", "R1336mzz(E)", "R124", "R1243zf",
    "R125", "R13", "R134a", "R13I1", "R14", "R141b", "R142b", "R143a",
    "R152A", "R161", "R21", "R218", "R22", "R227EA", "R23", "R236EA",
    "R236FA", "R245ca", "R245fa", "R32", "R365MFC", "R40", "R404A", "R407C",
    "R41", "R410A", "R507A", "RC318", "SES36", "SulfurDioxide",
    "SulfurHexafluoride", "Toluene", "Water", "Xenon", "cis-2-Butene",
    "m-Xylene", "n-Butane", "n-Decane", "n-Dodecane", "n-Heptane",
    "n-Hexane", "n-Nonane", "n-Octane", "n-Pentane", "n-Propane",
    "n-Undecane", "o-Xylene", "p-Xylene", "trans-2-Butene"
]


@app.route('/')
def index():
    return render_template('index.html', fluids=FLUIDS)


@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    try:
        fluid     = data['fluid']
        Tsource   = float(data['Tsource'])
        msource   = float(data['msource'])
        evappinch = float(data['evappinch'])
        evapeff   = float(data['evapeff'])
        Tsink     = float(data['Tsink'])
        condpinch = float(data['condpinch'])
        turbeff   = float(data['turbeff'])
        pumpeff   = float(data['pumpeff'])
        Uevap     = float(data['Uevap'])
        Ucond     = float(data['Ucond'])
        i_rate    = float(data['interest'])
        N         = float(data['lifetime'])
        n_op      = float(data['optime'])
        Cel       = float(data['price'])

        Cp = 4180

        # Cycle geometry
        T1  = Tsink + 10
        T3f = Tsource - (evappinch / (1 - (evapeff / 100)))
        Tpe = evappinch + T3f

        H3f = CP.PropsSI('H', 'T', T3f, 'Q', 0, fluid)
        S3f = CP.PropsSI('S', 'T', T3f, 'Q', 0, fluid)
        T3  = T3f
        P3  = CP.PropsSI('P', 'T', T3, 'Q', 1, fluid)
        H3  = CP.PropsSI('H', 'T', T3, 'Q', 1, fluid)
        S3  = CP.PropsSI('S', 'T', T3, 'Q', 1, fluid)

        # Pump
        P1 = CP.PropsSI('P', 'T', T1, 'Q', 0, fluid)
        H1 = CP.PropsSI('H', 'T', T1, 'Q', 0, fluid)
        V1 = 1 / CP.PropsSI('D', 'T', T1, 'Q', 0, fluid)
        S1 = CP.PropsSI('S', 'T', T1, 'Q', 0, fluid)

        dp = 0
        P2 = P3 / (1 - dp)
        P4 = P1 / (1 - dp)

        wpompag = (V1 * (P2 - P1)) / (pumpeff / 100)
        H2 = wpompag + H1
        T2 = CP.PropsSI('T', 'H', H2, 'P', P2, fluid)
        S2 = CP.PropsSI('S', 'H', H2, 'P', P2, fluid)

        # Turbine
        S4s = S3
        H4s = CP.PropsSI('H', 'S', S4s, 'P', P4, fluid)
        H4  = H3 - (turbeff / 100) * (H3 - H4s)
        S4  = CP.PropsSI('S', 'H', H4, 'P', P4, fluid)
        T4  = CP.PropsSI('T', 'H', H4, 'P', P4, fluid)
        X4  = CP.PropsSI('Q', 'H', H4, 'P', P4, fluid)

        # Energy balance
        Qb    = msource * Cp * (Tsource - Tpe)
        morc  = Qb / (H3 - H3f)
        Wt    = morc * (H3 - H4)
        Qo    = morc * (H3f - H2)
        Qevap = Qo + Qb
        Teout = Tsource - Qevap / (msource * Cp)
        Wp    = morc * (H2 - H1)
        Wnet  = Wt - Wp
        Eff   = (Wnet / Qevap) * 100

        # Turbine exit phase check
        if CP.PhaseSI('S', S4, 'T', T4, fluid) == 'gas':
            T1g = T1
            S1g = CP.PropsSI('S', 'Q', 1, 'T', T1g, fluid)
            H1g = CP.PropsSI('H', 'Q', 1, 'T', T1g, fluid)
        else:
            if fluid in {"R404A", "R407C"}:
                return jsonify({'error': 'Two-phase values for pseudo-pure substances (R404A, R407C) are not supported!'})
            T1g = T4
            H1g = H4
            S1g = CP.PropsSI('S', 'P', P3, 'H', H1g, fluid)

        Tpc   = T1g - condpinch
        msink = (morc * (H1g - H1)) / (Cp * (Tpc - Tsink))
        Qcond = morc * (H4 - H1)
        Tcout = Tsink + Qcond / (msink * Cp)
        Pratio = P3 / P4

        # Specific volumes
        V2 = 1 / CP.PropsSI('D', 'P', P2, 'H', H2, fluid)
        V3 = 1 / CP.PropsSI('D', 'T', T3, 'Q', 1, fluid)
        V4 = 1 / CP.PropsSI('D', 'P', P4, 'H', H4, fluid)

        # Reference state
        T0  = 298.15
        P0  = 100000
        S0  = CP.PropsSI('S', 'T', T0, 'P', P0, fluid)
        H0  = CP.PropsSI('H', 'T', T0, 'P', P0, fluid)

        # Source/sink water properties
        H5 = CP.PropsSI('H', 'T', Tsource, 'Q', 0, "Water")
        H6 = CP.PropsSI('H', 'T', Teout,   'Q', 0, "Water")
        S5 = CP.PropsSI('S', 'T', Tsource, 'Q', 0, "Water")
        S6 = CP.PropsSI('S', 'T', Teout,   'Q', 0, "Water")
        H7 = CP.PropsSI('H', 'T', Tsink,   'Q', 0, "Water")
        H8 = CP.PropsSI('H', 'T', Tcout,   'Q', 0, "Water")
        S7 = CP.PropsSI('S', 'T', Tsink,   'Q', 0, "Water")
        S8 = CP.PropsSI('S', 'T', Tcout,   'Q', 0, "Water")

        # Specific exergy (consistent with original)
        E1 = (H1 - H0) - (T0 * (S1 - S0))
        E2 = (H2 - H0) - (T0 * (S2 - S0))
        E3 = (H3 - H0) - (T0 * (S3 - S0))
        E4 = (H4 - H0) - (T0 * (S4 - S0))
        E5 = (H5 - H0) - (T0 * (S5 - S0))
        E6 = (H6 - H0) - (T0 * (S6 - S0))
        E7 = (H7 - H0) - (T0 * (S7 - S0))
        E8 = (H8 - H0) - (T0 * (S8 - S0))

        # Exergy destruction
        Ie       = msource * (E5 - E6) - morc * (E3 - E2)
        etaevap2 = ((morc * (E3 - E2)) / (msource * (E5 - E6))) * 100
        Ic       = morc * (E4 - E1) - msink * (E8 - E7)
        etacond2 = ((msink * (E8 - E7)) / (morc * (E4 - E1))) * 100
        It       = morc * (E3 - E4) - Wt
        etatur2  = (Wt / (morc * (E3 - E4))) * 100
        Ip       = morc * (E1 - E2) + Wp
        etapump2 = ((morc * (E2 - E1)) / Wp) * 100

        Exin      = (H5 - H6 - (T0 * (S5 - S6))) * msource
        etaexergy = (Wnet / Exin) * 100

        # Economic calculations
        dTlneva  = abs(((Tsource - T3) - (Teout - T2)) / log((Tsource - T3) / (Teout - T2)))
        Aeva     = Qevap / (Uevap * 1000 * dTlneva)
        CICEva   = 1010 * (Aeva) ** 0.8

        dTlncond = abs(((T4 - Tcout) - (T1 - Tsink)) / log((T4 - Tcout) / (T1 - Tsink)))
        Acond    = Qcond / (Ucond * 1000 * dTlncond)
        CICCond  = 516.62 * (Acond) ** 0.6
        CICPump  = 200 * (Wp / 1000) ** 0.65
        CICTurb  = 516.62 * (Wt / 1000) ** 0.75
        EIC      = CICEva + CICCond + CICPump + CICTurb
        FIC      = 1.75 * EIC
        CVC      = 0.05 * EIC
        TIC      = FIC + CVC

        inew = i_rate / 100
        CRF  = (inew * (1 + inew) ** N) / (((1 + inew) ** N) - 1)
        Zsc  = TIC
        CRC  = CRF * Zsc
        phi  = (1.5 / 100) * Zsc
        LCOE = (CRC + phi) / ((Wnet / 1000) * n_op)

        a_pb = (Wnet / 1000) * n_op * Cel - phi
        b_pb = a_pb - (inew * Zsc)
        PB   = log10(a_pb / b_pb) / log10(1 + inew)
        SIC  = EIC / (Wnet / 1000)

        # Phase and quality at each state
        phase1 = CP.PhaseSI('T', T1, 'Q', 0, fluid)
        phase2 = CP.PhaseSI('S', S2, 'T', T2, fluid)
        phase3 = CP.PhaseSI('T', T3, 'Q', 1, fluid)
        phase4 = CP.PhaseSI('S', S4, 'T', T4, fluid)
        X1 = 0.0
        X2 = CP.PropsSI('Q', 'H', H2, 'P', P2, fluid)
        X3 = 1.0
        X4_disp = X4

        # Generate T-S diagram
        T_list = [T1, T2, T3, T4]
        S_list = [S1, S2, S3, S4]

        pp = PropertyPlot(fluid, 'TS', unit_system='EUR', tp_limits='ORC')
        pp.calc_isolines(CoolProp.iQ, num=11)
        cycle = StateContainer()
        if T4 == T1g:
            cycle[0, "T"] = T_list[0]; cycle[0, "S"] = S_list[0]
            cycle[1, "T"] = T_list[1]; cycle[1, "S"] = S_list[1]
            cycle[3, "T"] = T3f;       cycle[3, "S"] = S3f
            cycle[4, "T"] = T_list[2]; cycle[4, "S"] = S_list[2]
            cycle[5, "T"] = T_list[3]; cycle[5, "S"] = S_list[3]
            cycle[6, "T"] = T_list[0]; cycle[6, "S"] = S_list[0]
        else:
            cycle[0, "T"] = T_list[0]; cycle[0, "S"] = S_list[0]
            cycle[1, "T"] = T_list[1]; cycle[1, "S"] = S_list[1]
            cycle[3, "T"] = T3f;       cycle[3, "S"] = S3f
            cycle[4, "T"] = T_list[2]; cycle[4, "S"] = S_list[2]
            cycle[5, "T"] = T_list[3]; cycle[5, "S"] = S_list[3]
            cycle[6, "T"] = T1g;       cycle[6, "S"] = S1g
            cycle[7, "T"] = T_list[0]; cycle[7, "S"] = S_list[0]

        pp.draw_process(cycle)
        pp.show()
        pp.figure.set_size_inches(6, 5)

        buf = io.BytesIO()
        pp.figure.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        plot_b64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close('all')

        return jsonify({
            'success': True,
            'plot': plot_b64,
            'summary': {
                'eta_thermal': round(Eff, 4),
                'eta_exergy':  round(etaexergy, 4),
                'Wnet':  round(Wnet, 2),
                'EIC':   round(EIC, 2),
                'FIC':   round(FIC, 2),
                'TIC':   round(TIC, 2),
                'CRF':   round(CRF, 4),
                'CRC':   round(CRC, 2),
                'LCOE':  round(LCOE, 4),
                'SIC':   round(SIC, 2),
                'PB':    round(PB, 2),
            },
            'states': [
                {'state': 1, 'T': round(T1, 2), 'P': round(P1, 2), 'V': f'{V1:.8f}', 'H': round(H1, 1), 'S': round(S1, 4), 'phase': phase1, 'X': f'{X1:.4f}'},
                {'state': 2, 'T': round(T2, 2), 'P': round(P2, 2), 'V': f'{V2:.8f}', 'H': round(H2, 1), 'S': round(S2, 4), 'phase': phase2, 'X': f'{X2:.4f}'},
                {'state': 3, 'T': round(T3, 2), 'P': round(P3, 2), 'V': f'{V3:.8f}', 'H': round(H3, 1), 'S': round(S3, 4), 'phase': phase3, 'X': f'{X3:.4f}'},
                {'state': 4, 'T': round(T4, 2), 'P': round(P4, 2), 'V': f'{V4:.8f}', 'H': round(H4, 1), 'S': round(S4, 4), 'phase': phase4, 'X': f'{X4_disp:.4f}'},
            ],
            'performance': {
                'morc':         round(morc, 4),
                'msink':        round(msink, 4),
                'Qo':           round(Qo, 2),
                'Qb':           round(Qb, 2),
                'Qevap':        round(Qevap, 2),
                'Qcond':        round(Qcond, 2),
                'Teout':        round(Teout, 2),
                'Tcout':        round(Tcout, 2),
                'Wp':           round(Wp, 2),
                'Wt':           round(Wt, 2),
                'Pratio':       round(Pratio, 2),
                'Wnet':         round(Wnet, 2),
                'eta_thermal':  round(Eff, 2),
            },
            'exergy': {
                'etaevap2':  round(etaevap2, 2),
                'etacond2':  round(etacond2, 2),
                'etatur2':   round(etatur2, 2),
                'etapump2':  round(etapump2, 2),
                'Ie':        round(Ie, 2),
                'Ic':        round(Ic, 2),
                'It':        round(It, 2),
                'Ip':        round(Ip, 2),
                'Exin':      round(Exin, 4),
                'etaexergy': round(etaexergy, 2),
            }
        })

    except Exception as e:
        return jsonify({'error': f'Cycle cannot be completed! {str(e)}'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
