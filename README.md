---
title: NeuORC v1.2
emoji: ⚡
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: gpl-3.0
---

# NeuORC v1.2 – Organic Rankine Cycle Calculator

**Try it online → [NeuORC on Hugging Face Spaces](https://huggingface.co/spaces/Berkovski/NeuORC)**

NeuORC is an educational web application for thermodynamic analysis of Organic Rankine Cycle (ORC) systems for waste heat recovery and geothermal energy applications. It calculates energy, exergy, and economic performance using 124 working fluids from the CoolProp library.

## Features

- Thermodynamic cycle analysis (energy & exergy)
- Economic analysis: EIC, FIC, TIC, LCOE, payback period
- T-S diagram generation
- 124 working fluids via CoolProp
- SI unit system with °C / K input support

## Running Locally

```bash
git clone https://github.com/arcilyes/NeuORC.git
cd NeuORC
pip install -r requirements.txt
python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Dependencies

- CoolProp == 6.6.0
- matplotlib >= 3.7.0
- Flask >= 2.3.0

## Assumptions

- Heat source and cooling flow fluids are assumed to be water.
- Ambient temperature is taken as 25 °C; cooling flow temperatures below 25 °C will yield negative exergy efficiency values.

## License

GNU GPL v3 — Mehmet Berk Azdural
Academic Advisors: Prof. Ali Kahraman, Asst. Prof. Sadık Ata
Necmettin Erbakan University
