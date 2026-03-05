import React from "react";

export default function EventsTable({ events, filters }) {

  // Безопасный парсинг даты
  function parseDate(dateStr) {
    if (!dateStr) return "-";
    // убираем микросекунды и добавляем Z для корректного UTC
    const clean = dateStr.split(".")[0] + "Z";
    const d = new Date(clean);
    return isNaN(d) ? "-" : d.toLocaleString();
  }

  // Фильтрация
  const filteredEvents = events.filter((event) => {
    const mainSeverity = event.severity.split(",")[0].trim();

    const matchSeverity =
      filters.severity === "all" || mainSeverity === filters.severity;

    const matchSensor =
      !filters.sensor_id || event.sensor_id.includes(filters.sensor_id);

    const matchDate =
      (!filters.dateFrom || new Date(event.created_at) >= new Date(filters.dateFrom)) &&
      (!filters.dateTo || new Date(event.created_at) <= new Date(filters.dateTo));

    return matchSeverity && matchSensor && matchDate;
  });

  // Получаем главное значение severity для цвета строки
  function getRowClass(severity) {
    const mainSeverity = severity.split(",")[0].trim();
    switch (mainSeverity) {
      case "normal":
        return "normal";
      case "warning":
        return "warning";
      case "critical":
        return "critical";
      default:
        return "";
    }
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Time</th>
          <th>Sensor ID</th>
          <th>Location</th>
          <th>Temperature</th>
          <th>Humidity</th>
          <th>Severity</th>
          <th>Notification</th>
        </tr>
      </thead>
      <tbody>
        {filteredEvents.map((e, idx) => (
          <tr key={idx} className={getRowClass(e.severity)}>
            <td>{parseDate(e.created_at)}</td>
            <td>{e.sensor_id}</td>
            <td>{e.location}</td>
            <td>{e.temperature}</td>
            <td>{e.humidity}</td>
            <td>{e.severity}</td>
            <td>{e.notification_sent ? "Yes" : "No"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}