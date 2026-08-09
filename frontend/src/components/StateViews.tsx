import { AlertCircle, Inbox } from "lucide-react";

export function LoadingState() {
  return (
    <div className="flex h-64 items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand border-t-transparent" />
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="glass-card flex items-center gap-3 border-pulse-risk/30 p-5 text-sm text-pulse-risk">
      <AlertCircle className="h-4 w-4 shrink-0" />
      {message}
    </div>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="glass-card flex flex-col items-center gap-2 p-10 text-center text-sm text-ink-muted">
      <Inbox className="h-6 w-6" />
      {message}
    </div>
  );
}
