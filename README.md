# QGIS Sustainability Toolkit

> **A QGIS plugin to evaluate multi-dimensional sustainability metrics (economic, environmental, and social), providing automatic recommendations for improvement.**

![License](https://img.shields.io/badge/license-GPLv2-blue.svg)
![QGIS Version](https://img.shields.io/badge/QGIS-3.x-green.svg)
![Python Version](https://img.shields.io/badge/Python-3.7%2B-yellow.svg)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Interface & Workflows](#interface--workflows)
  - [Example Indicators](#example-indicators)
- [Screenshots](#screenshots)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Overview

**QGIS Sustainability Toolkit** is a plugin designed to simplify and automate the evaluation of sustainability across three pillars:
1. **Economy** – e.g., infrastructures, revenues, tourism.
2. **Environment** – e.g., biodiversity, resources, landscapes, climate.
3. **Society** – e.g., security, traditions, hospitality, unemployment rate.

It calculates key metrics for multiple time periods (T1, T2, T3) and outputs whether the project or region is deemed **“Durable”** or **“Non durable.”** If results show any “Non durable” status, the plugin generates recommended solutions or best practices to address identified issues (e.g., investing locally, preserving biodiversity, improving safety, etc.).

---

## Features

- **Multi-Tab Interface:** Separate tabs for different time periods (T1, T2, T3).
- **Sustainability Metrics:** Automated calculation of normalized values and factor impacts for various indicators (economic, environmental, and societal).
- **Decision & Recommendations:** Displays final verdict for each period and offers tailored solutions if certain thresholds are not met.
- **QGIS Integration:** Easily accessible from the QGIS Plugins menu; leverages Python and QGIS APIs for a smooth geospatial workflow.
- **Extensible:** Additional indicators or custom factors can be added with minimal code modifications.

---

## Installation

1. **Download or Clone:**  
   ```bash
   git clone https://github.com/YourUserName/qgis-sustainability-toolkit.git
