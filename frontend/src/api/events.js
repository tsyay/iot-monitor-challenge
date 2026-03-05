export async function fetchEvents() {
  const res = await fetch('/api/events');
  if (!res.ok) throw new Error('Ошибка загрузки событий');
  return res.json();
}

export async function simulateSensor(payload) {
  const res = await fetch('/webhooks/sensor', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Ошибка симуляции датчика');
  return res.json();
}