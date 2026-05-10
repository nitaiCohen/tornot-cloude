export function getMondayOfWeek(date: Date): Date {
  const d = new Date(date);
  const day = d.getDay(); // 0=Sun
  const diff = day === 0 ? -6 : 1 - day;
  d.setDate(d.getDate() + diff);
  d.setHours(0, 0, 0, 0);
  return d;
}

export function addDays(date: Date, n: number): Date {
  const d = new Date(date);
  d.setDate(d.getDate() + n);
  return d;
}

export function toISO(date: Date): string {
  return date.toISOString().slice(0, 10);
}

export function formatHE(date: Date): string {
  return date.toLocaleDateString('he-IL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

export function weekStatus(monday: Date): 'past' | 'current' | 'future' {
  const todayMon = getMondayOfWeek(new Date());
  const diff = monday.getTime() - todayMon.getTime();
  if (diff < 0) return 'past';
  if (diff === 0) return 'current';
  return 'future';
}

export const STATUS_LABELS: Record<string, string> = {
  past: 'בוצע',
  current: 'נוכחי',
  future: 'מתוכנן',
};
