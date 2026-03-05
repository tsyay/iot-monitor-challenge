import React from "react";

export default function Filters({ filters, setFilters }) {
  return (
    <div className="filters">
      <select
        value={filters.severity}
        onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
      >
        <option value="all">Все уровни</option>
        <option value="normal">Normal</option>
        <option value="warning">Warning</option>
        <option value="critical">Critical</option>
      </select>

      <input
        type="text"
        placeholder="Sensor ID"
        value={filters.sensor_id}
        onChange={(e) => setFilters({ ...filters, sensor_id: e.target.value })}
      />

      <input
        type="date"
        value={filters.dateFrom}
        onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
      />

      <input
        type="date"
        value={filters.dateTo}
        onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
      />
    </div>
  );
}