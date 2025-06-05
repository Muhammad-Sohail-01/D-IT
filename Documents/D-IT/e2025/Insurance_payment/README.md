<a id="readme-top"></a>

<!-- PROJECT BANNER -->
<div align="center">
  <a href="https://befst.ai">
    <img src="https://via.placeholder.com/1200x300.png?text=Your+Banner+Here" alt="Project Banner" width="100%">
  </a>
</div>

<h3 align="center">Insurance Payment Module</h3>
<p align="center">
  This Odoo module manages insurance payments, integrating seamlessly with the Sales and Accounting modules to enhance your workflow.
  <br />
  <a href="https://befst.ai"><strong>Explore Befst Profile »</strong></a>
  <br />
  <br />
  <a href="#">View Demo</a> · 
  <a href="#">Report Bug</a> · 
  <a href="#">Request Feature</a>
</p>

---

## Table of Contents
<details>
  <summary>Click to expand</summary>
  <ol>
    <li><a href="#overview">Overview</a></li>
    <li><a href="#features">Features</a></li>
    <li><a href="#dependencies">Dependencies</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#usage-guide">Usage Guide</a></li>
    <ul>
      <li><a href="#setting-up-insurance-companies">Setting Up Insurance Companies</a></li>
      <li><a href="#managing-insurance-transactions">Managing Insurance Transactions</a></li>
      <li><a href="#generating-insurance-journal-entries">Generating Insurance Journal Entries</a></li>
    </ul>
    <li><a href="#testing-the-journal-entry-flow">Testing the Journal Entry Flow</a></li>
    <li><a href="#screenshots">Screenshots</a></li>
    <li><a href="#support">Support</a></li>
    <li><a href="#license-and-copyright">License and Copyright</a></li>
  </ol>
</details>

---

## Overview

The **Insurance Payment Module** allows businesses to manage insurance payments seamlessly within Odoo. It extends the sale.order model by introducing insurance-related fields and functionality, enabling tracking, automated calculations, journal entry creation, and integration with existing accounting workflows.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Features

- Manage insurance companies and related policies effortlessly.
- Automate calculations for insurance amounts based on fixed values or percentages.
- Generate and post insurance-related journal entries.
- User-friendly interface enhancements for managing insurance details in sales orders.
- Seamless integration with existing accounting and sales workflows.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Dependencies

This module requires the following Odoo modules to function correctly:

- `base`
- `account`
- `sale`
- `sale_management`
- `tk_vehicle_management` (custom module)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Installation

1. **Clone or Download the Repository**  
   Place the module folder into your Odoo addons directory.

2. **Restart the Odoo Server**
   ```bash
   ./odoo-bin -u all
