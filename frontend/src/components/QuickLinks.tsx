import React from 'react';

const links = [
  { label: "USITC HTS", url: "https://hts.usitc.gov/" },
  { label: "USITC DataWeb", url: "https://dataweb.usitc.gov/" },
  { label: "WTO Tariff Data", url: "https://ta.wto.org/" },
  { label: "WTO Tariff Data (alt)", url: "https://www.wto.org/english/tratop_e/tariffs_e/tariff_data_e.htm" },
  { label: "UN Comtrade", url: "https://comtrade.un.org/data/" },
  { label: "WCO HS Nomenclature", url: "http://www.wcoomd.org/en/topics/nomenclature/instrument-and-tools/hs-nomenclature-2022-edition.aspx" },
  { label: "Data.gov HTS", url: "https://catalog.data.gov/dataset?q=harmonized+tariff+schedule" },
  { label: "WTO HS Tracker (About)", url: "https://hstracker.wto.org/?_inputs_&sidebarCollapsed=false&page=%22about%22" },
  { label: "WTO HS Tracker (Visualizer)", url: "https://hstracker.wto.org/?_inputs_&sidebarCollapsed=false&page=%22visualizer%22&hscode=%22%22" },
  { label: "WTO HS Tracker (At a Glance)", url: "https://hstracker.wto.org/?_inputs_&page=%22glance%22&sidebarCollapsed=false&hscode=%22%22" },
  { label: "Cartage AI HTS Code Lookup", url: "https://www.cartage.ai/tools/hts-code-lookup" },
];

export default function QuickLinks() {
  return (
    <div className="quick-links-glass">
      <h2>🌐 Quick Links & Resources</h2>
      <div className="quick-links-list">
        {links.map(link => (
          <a
            key={link.url}
            href={link.url}
            target="_blank"
            rel="noopener noreferrer"
            className="quick-link-card"
          >
            {link.label}
          </a>
        ))}
      </div>
    </div>
  );
} 