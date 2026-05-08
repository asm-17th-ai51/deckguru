'use client';

import { usePatchInfoQuery } from '@/api/get-patch-info/query';
import { Badge } from '@/components/ui/badge';
import type { PatchInfo } from '@/lib/schema';

const FALLBACK_PATCH_INFO: PatchInfo = {
  patch_version: 'unknown',
  last_updated: 'unknown',
  warnings: ['patch_info_unavailable'],
};

const formatLastUpdated = (value: string) => {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toISOString().slice(0, 10);
};

export function PatchStatusHeader() {
  const { data, isError } = usePatchInfoQuery();
  const patchInfo = data ?? FALLBACK_PATCH_INFO;
  const hasWarnings = data ? patchInfo.warnings.length > 0 : isError;

  return (
    <header className="absolute inset-x-0 top-0 z-20 flex justify-center p-4 sm:justify-end sm:p-6">
      <div className="grid max-w-full grid-cols-1 justify-items-center gap-2 sm:flex sm:flex-row sm:flex-wrap sm:justify-end">
        {hasWarnings ? (
          <Badge
            variant="destructive"
            className="h-auto border-2 px-3 py-2 text-[10px]">
            DATA WARNING
          </Badge>
        ) : null}
        <Badge
          variant="outline"
          className="h-auto border-2 px-3 py-2 text-[10px] backdrop-blur">
          PATCH VERSION {patchInfo.patch_version}
        </Badge>
        <Badge
          variant="outline"
          className="h-auto border-2 px-3 py-2 text-[10px] backdrop-blur">
          LAST UPDATED {formatLastUpdated(patchInfo.last_updated)}
        </Badge>
      </div>
    </header>
  );
}
