export interface FetchedTimeInfo {
  formattedDate: string;
  relative: string;
  fullLabel: string;
}

/**
 * Formats an ISO date/timestamp into:
 * formattedDate: "15 Nov 2026, 02:30 PM"
 * relative: "15 mins ago" / "Just now" / "2 hours ago" / "Yesterday" / "3 days ago"
 * fullLabel: "Fetched: 15 Nov 2026, 02:30 PM (15 mins ago)"
 */
export function formatFetchedTimestamp(dateStr?: string | null): FetchedTimeInfo | null {
  if (!dateStr) return null;
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return null;

  const day = String(date.getDate()).padStart(2, '0');
  const month = date.toLocaleString('en-US', { month: 'short' });
  const year = date.getFullYear();
  const time = date.toLocaleString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });
  const formattedDate = `${day} ${month} ${year}, ${time}`;

  const diffMs = Math.max(0, Date.now() - date.getTime());
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  let relative = 'Just now';
  if (diffSec < 45) {
    relative = 'Just now';
  } else if (diffMin === 1) {
    relative = '1 min ago';
  } else if (diffMin < 60) {
    relative = `${diffMin} mins ago`;
  } else if (diffHour === 1) {
    relative = '1 hour ago';
  } else if (diffHour < 24) {
    relative = `${diffHour} hours ago`;
  } else if (diffDay === 1) {
    relative = 'Yesterday';
  } else {
    relative = `${diffDay} days ago`;
  }

  return {
    formattedDate,
    relative,
    fullLabel: `Fetched: ${formattedDate} (${relative})`,
  };
}
