import { Badge } from '@/components/ui/badge';

export function PatchStatusHeader() {
  return (
    <header className="absolute top-0 right-0 z-20 flex justify-end p-4 sm:p-6">
      <div className="flex flex-row gap-2">
        <Badge variant="outline" className="h-auto border-2 px-3 py-2">
          PATCH VERSION 14.9
        </Badge>
        <Badge variant="outline" className="h-auto border-2 px-3 py-2">
          LAST UPDATED 2026-05-04
        </Badge>
      </div>
    </header>
  );
}
